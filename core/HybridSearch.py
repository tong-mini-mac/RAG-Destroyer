import math
import re


_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "do", "for", "from", "how",
    "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "was", "what",
    "when", "where", "which", "who", "why", "with", "you", "your",
}


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"[A-Za-z0-9]{2,}", (text or "").lower())
    return {w for w in words if w not in _STOPWORDS}


class HybridSearchEngine:
    """
    Lightweight hybrid reranker (V3 scaffold):
    - lexical score from deterministic SearchWorker relevance/hit_count
    - semantic proxy score from token overlap between query and doc metadata
    """

    def __init__(self, *, alpha: float = 0.65, top_k: int = 5):
        self.alpha = max(0.0, min(1.0, float(alpha)))
        self.top_k = max(1, int(top_k))

    @staticmethod
    def _semantic_proxy_score(query: str, doc: dict) -> float:
        q = _tokenize(query)
        if not q:
            return 0.0
        doc_text = " ".join(
            [
                str(doc.get("title", "")),
                str(doc.get("summary", "")),
                " ".join(str(t) for t in (doc.get("tags") or [])),
            ]
        )
        d = _tokenize(doc_text)
        if not d:
            return 0.0
        inter = len(q & d)
        return inter / math.sqrt(len(q) * len(d))

    def rerank(self, query: str, search_results: list[dict]) -> list[dict]:
        # Collapse duplicates across keyword workers first.
        merged: dict[str, dict] = {}
        for item in search_results or []:
            for hit in item.get("hits", []):
                path = hit.get("path")
                if not path:
                    continue
                if path not in merged:
                    merged[path] = dict(hit)
                    merged[path]["hit_count"] = 1
                else:
                    merged[path]["relevance"] = merged[path].get("relevance", 0) + hit.get("relevance", 0)
                    merged[path]["hit_count"] = merged[path].get("hit_count", 1) + 1

        docs = list(merged.values())
        if not docs:
            return []

        max_lex = max(float(d.get("relevance", 0)) for d in docs) or 1.0
        max_hit = max(float(d.get("hit_count", 0)) for d in docs) or 1.0

        for d in docs:
            lex_norm = 0.75 * (float(d.get("relevance", 0)) / max_lex) + 0.25 * (
                float(d.get("hit_count", 0)) / max_hit
            )
            sem_norm = self._semantic_proxy_score(query, d)
            d["hybrid_score"] = self.alpha * lex_norm + (1.0 - self.alpha) * sem_norm

        docs.sort(
            key=lambda x: (
                float(x.get("hybrid_score", 0.0)),
                float(x.get("hit_count", 0)),
                float(x.get("relevance", 0)),
            ),
            reverse=True,
        )
        return docs[: self.top_k]

    def rerank_vector_only(self, query: str, vector_hits: list[dict]) -> list[dict]:
        """Rerank results from VectorIndex.query() with semantic proxy + department boosts."""
        if not vector_hits:
            return []

        docs = [dict(h) for h in vector_hits]
        max_vec = max(float(d.get("vector_score", 0)) for d in docs) or 1.0

        for d in docs:
            vec_norm = float(d.get("vector_score", 0)) / max_vec
            sem_norm = self._semantic_proxy_score(query, d)
            d["hybrid_score"] = self.alpha * vec_norm + (1.0 - self.alpha) * sem_norm

        docs.sort(key=lambda x: float(x.get("hybrid_score", 0.0)), reverse=True)
        return docs[: self.top_k]
