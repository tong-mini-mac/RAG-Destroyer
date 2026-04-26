from __future__ import annotations

import json
import math
import os
import re
from datetime import datetime

import frontmatter
import numpy as np

from .Chunking import chunk_markdown_text
from .Utils import CONFIG, document_visible_to_viewer
from .sources import build_knowledge_source

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "do", "for", "from", "how",
    "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "was", "what",
    "when", "where", "which", "who", "why", "with", "you", "your",
}


def _tokenize(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z0-9]{2,}", (text or "").lower())
    return [w for w in words if w not in _STOPWORDS]


def _cosine_from_token_sets(q_tokens: set[str], d_tokens: set[str]) -> float:
    if not q_tokens or not d_tokens:
        return 0.0
    inter = len(q_tokens & d_tokens)
    return inter / math.sqrt(len(q_tokens) * len(d_tokens))


def _cosine_dense(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two 1-D numpy arrays."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


# ── lazy-loaded ONNX model ──────────────────────────────────────────
_ONNX_MODEL = None
_ONNX_MODEL_NAME = "all-MiniLM-L6-v2"


def _get_onnx_model():
    global _ONNX_MODEL
    if _ONNX_MODEL is None:
        from sentence_transformers import SentenceTransformer
        _ONNX_MODEL = SentenceTransformer(_ONNX_MODEL_NAME)
    return _ONNX_MODEL


class VectorIndex:
    """
    Lightweight local vector-like index using token sets.
    - chunks all markdown docs with metadata
    - excludes table/code chunks from vector candidates
    - supports ACL inheritance at parent (document) level
    """

    def __init__(self, vault_path=None):
        self.vault_path = vault_path or CONFIG["CLEANED_DATA_PATH"]
        self.source = build_knowledge_source(
            CONFIG.get("KNOWLEDGE_SOURCE_BACKEND", "localfs"),
            self.vault_path,
        )
        self._vectors_dir = os.path.join(self.vault_path, "_vectors")
        os.makedirs(self._vectors_dir, exist_ok=True)
        self.chunk_index_path = os.path.join(self._vectors_dir, "_chunks.json")
        self.vector_index_path = os.path.join(self._vectors_dir, "_index.json")
        self.embedding_index_path = os.path.join(self._vectors_dir, "_embeddings.npy")
        self.embedding_meta_path = os.path.join(self._vectors_dir, "_embedding_meta.json")
        self.enable_onnx = str(CONFIG.get("SAG_ENABLE_ONNX_EMBEDDING", "False")).lower() == "true"

    def build(self) -> tuple[int, int]:
        chunk_target = int(CONFIG.get("SAG_CHUNK_TARGET_CHARS", 900))
        chunk_min = int(CONFIG.get("SAG_CHUNK_MIN_CHARS", 800))
        chunk_max = int(CONFIG.get("SAG_CHUNK_MAX_CHARS", 1000))
        chunk_overlap = int(CONFIG.get("SAG_CHUNK_OVERLAP_CHARS", 120))

        chunks: list[dict] = []
        vectors: list[dict] = []
        for dept in self.source.list_departments():
            dept_root = os.path.join(self.vault_path, dept)
            for file_path in self.source.iter_markdown_files(dept):
                try:
                    post = frontmatter.load(file_path)
                except Exception:
                    continue
                rel_path = os.path.relpath(file_path, dept_root).replace("\\", "/")
                basename = os.path.basename(file_path)
                doc_id = str(post.get("doc_id", "N/A"))
                title = str(post.get("title", basename.replace(".md", "")))
                summary = str(post.get("summary", ""))
                tags = post.get("tags", [])
                if not isinstance(tags, list):
                    tags = [str(tags)]
                audience = post.get("audience")
                updated_at = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()

                chunked = chunk_markdown_text(
                    post.content or "",
                    target_chars=chunk_target,
                    min_chars=chunk_min,
                    max_chars=chunk_max,
                    overlap_chars=chunk_overlap,
                )
                for i, part in enumerate(chunked, start=1):
                    content_type = part.get("content_type", "text")
                    vector_eligible = content_type == "text"
                    chunk_id = f"{doc_id}.{i}"
                    chunk = {
                        "doc_id": doc_id,
                        "parent_id": doc_id,
                        "chunk_id": chunk_id,
                        "chunk_order": i,
                        "content_type": content_type,
                        "vector_eligible": vector_eligible,
                        "acl_policy_ref": doc_id,
                        "department": dept,
                        "tags": tags,
                        "source_path": rel_path,
                        "basename": basename,
                        "audience": audience,
                        "updated_at": updated_at,
                        "title": title,
                        "summary": summary,
                        "content": part.get("content", ""),
                    }
                    chunks.append(chunk)
                    if vector_eligible:
                        vec_text = " ".join([title, summary, " ".join(str(t) for t in tags), chunk["content"]])
                        vectors.append(
                            {
                                "chunk_id": chunk_id,
                                "doc_id": doc_id,
                                "department": dept,
                                "source_path": rel_path,
                                "basename": basename,
                                "audience": audience,
                                "title": title,
                                "summary": summary,
                                "tags": tags,
                                "tokens": sorted(set(_tokenize(vec_text))),
                            }
                        )

        with open(self.chunk_index_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        with open(self.vector_index_path, "w", encoding="utf-8") as f:
            json.dump(vectors, f, ensure_ascii=False, indent=2)

        # ── ONNX dense embedding generation ──────────────────────
        if self.enable_onnx and vectors:
            try:
                texts = [
                    " ".join([v.get("title", ""), v.get("summary", ""), " ".join(str(t) for t in v.get("tags", []))])
                    for v in vectors
                ]
                model = _get_onnx_model()
                embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
                np.save(self.embedding_index_path, embeddings)

                meta = [
                    {
                        "chunk_id": v["chunk_id"],
                        "doc_id": v["doc_id"],
                        "department": v["department"],
                    }
                    for v in vectors
                ]
                with open(self.embedding_meta_path, "w", encoding="utf-8") as f:
                    json.dump(meta, f, ensure_ascii=False, indent=2)
            except Exception as exc:
                import logging
                logging.warning("ONNX embedding build failed: %s", exc)

        return len(chunks), len(vectors)

    def _load_indexes(self) -> tuple[list[dict], list[dict]]:
        if not os.path.isfile(self.chunk_index_path) or not os.path.isfile(self.vector_index_path):
            return [], []
        try:
            with open(self.chunk_index_path, "r", encoding="utf-8") as f:
                chunks = json.load(f)
            with open(self.vector_index_path, "r", encoding="utf-8") as f:
                vectors = json.load(f)
            if not isinstance(chunks, list) or not isinstance(vectors, list):
                return [], []
            return chunks, vectors
        except (json.JSONDecodeError, OSError, ValueError, TypeError):
            return [], []

    def _load_onnx_embeddings(self) -> tuple[np.ndarray | None, list[dict] | None]:
        """Load ONNX .npy embeddings + metadata. Returns (embeddings, meta) or (None, None)."""
        if not os.path.isfile(self.embedding_index_path) or not os.path.isfile(self.embedding_meta_path):
            return None, None
        try:
            embeddings = np.load(self.embedding_index_path)
            with open(self.embedding_meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            return embeddings, meta
        except Exception:
            return None, None

    def query(
        self,
        query: str,
        allowed_subsets,
        viewer_role: str | None = None,
        viewer_active_department: str | None = None,
        top_k: int | None = None,
    ) -> list[dict]:
        chunks, vectors = self._load_indexes()
        if not chunks or not vectors:
            return []

        allowed = None if allowed_subsets == "ALL" else set(allowed_subsets or [])
        top_k = int(top_k or CONFIG.get("SAG_VECTOR_TOP_K", 8))

        # ── try ONNX dense path ──────────────────────────────────
        onnx_embs, onnx_meta = self._load_onnx_embeddings()
        if self.enable_onnx and onnx_embs is not None and onnx_meta is not None:
            return self._query_onnx(query, vectors, onnx_embs, onnx_meta, allowed, top_k)

        # ── fallback: token-set cosine ───────────────────────────
        q_tokens = set(_tokenize(query))
        if not q_tokens:
            return []

        scored: list[tuple[float, dict]] = []
        for v in vectors:
            dept = v.get("department")
            if allowed is not None and dept not in allowed:
                continue
            if viewer_role is not None and not document_visible_to_viewer(
                viewer_role,
                dept,
                v.get("basename", ""),
                v.get("audience"),
                viewer_active_department,
            ):
                continue
            score = _cosine_from_token_sets(q_tokens, set(v.get("tokens", [])))
            if score > 0:
                scored.append((score, v))
        if not scored:
            return []
        scored.sort(key=lambda x: x[0], reverse=True)
        top_hits = scored[:top_k]

        # sibling expansion from chunk index
        chunks_by_doc: dict[str, list[dict]] = {}
        for c in chunks:
            chunks_by_doc.setdefault(str(c.get("doc_id", "")), []).append(c)
        for d in chunks_by_doc.values():
            d.sort(key=lambda x: int(x.get("chunk_order", 0)))

        doc_best: dict[str, dict] = {}
        for score, hit in top_hits:
            doc_id = str(hit.get("doc_id"))
            if doc_id not in doc_best or score > doc_best[doc_id]["_score"]:
                doc_best[doc_id] = {"_score": score, "_hit": hit}

        out: list[dict] = []
        for doc_id, item in doc_best.items():
            hit = item["_hit"]
            dept = hit.get("department")
            source_path = hit.get("source_path")
            full_path = os.path.join(self.vault_path, dept, source_path) if dept and source_path else ""

            sibs = chunks_by_doc.get(doc_id, [])
            table_neighbors = sum(1 for c in sibs if c.get("content_type") == "table")
            out.append(
                {
                    "path": full_path,
                    "title": hit.get("title", source_path),
                    "relevance": int(round(item["_score"] * 10)),
                    "department": dept,
                    "tags": hit.get("tags", []),
                    "summary": hit.get("summary", ""),
                    "doc_id": doc_id,
                    "vector_score": item["_score"],
                    "sibling_table_chunks": table_neighbors,
                }
            )
        out.sort(key=lambda x: float(x.get("vector_score", 0.0)), reverse=True)
        return out

    # ── ONNX dense query ──────────────────────────────────────────────
    def _query_onnx(
        self,
        query: str,
        vectors: list[dict],
        onnx_embs: np.ndarray,
        onnx_meta: list[dict],
        allowed: set | None,
        top_k: int,
    ) -> list[dict]:
        try:
            model = _get_onnx_model()
            q_vec = model.encode([query], normalize_embeddings=True)[0]
        except Exception:
            return []

        scored: list[tuple[float, dict]] = []
        for i, v in enumerate(vectors):
            dept = v.get("department")
            if allowed is not None and dept not in allowed:
                continue
            if i >= len(onnx_embs):
                continue
            score = _cosine_dense(q_vec, onnx_embs[i])
            if score > 0:
                scored.append((score, v))

        if not scored:
            return []
        scored.sort(key=lambda x: x[0], reverse=True)
        top_hits = scored[:top_k]

        # load chunks for sibling expansion
        chunks, _ = self._load_indexes()
        chunks_by_doc: dict[str, list[dict]] = {}
        for c in chunks:
            chunks_by_doc.setdefault(str(c.get("doc_id", "")), []).append(c)
        for d in chunks_by_doc.values():
            d.sort(key=lambda x: int(x.get("chunk_order", 0)))

        doc_best: dict[str, dict] = {}
        for score, hit in top_hits:
            doc_id = str(hit.get("doc_id"))
            if doc_id not in doc_best or score > doc_best[doc_id]["_score"]:
                doc_best[doc_id] = {"_score": score, "_hit": hit}

        out: list[dict] = []
        for doc_id, item in doc_best.items():
            hit = item["_hit"]
            dept = hit.get("department")
            source_path = hit.get("source_path")
            full_path = os.path.join(self.vault_path, dept, source_path) if dept and source_path else ""

            sibs = chunks_by_doc.get(doc_id, [])
            table_neighbors = sum(1 for c in sibs if c.get("content_type") == "table")
            out.append(
                {
                    "path": full_path,
                    "title": hit.get("title", source_path),
                    "relevance": int(round(item["_score"] * 10)),
                    "department": dept,
                    "tags": hit.get("tags", []),
                    "summary": hit.get("summary", ""),
                    "doc_id": doc_id,
                    "vector_score": item["_score"],
                    "sibling_table_chunks": table_neighbors,
                }
            )
        out.sort(key=lambda x: float(x.get("vector_score", 0.0)), reverse=True)
        return out
