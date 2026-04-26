from __future__ import annotations

import re


def detect_content_type(text: str) -> str:
    body = (text or "").strip()
    if not body:
        return "text"
    if "```" in body:
        return "code"

    lines = [ln.rstrip() for ln in body.splitlines() if ln.strip()]
    if len(lines) >= 2:
        has_pipes = any("|" in ln for ln in lines[:4])
        has_md_table_sep = any(re.search(r"^\s*\|?[\s:-]+\|[\s|:-]*$", ln) for ln in lines)
        if has_pipes and has_md_table_sep:
            return "table"
    return "text"


def _split_sentences(text: str) -> list[str]:
    raw = re.split(r"(?<=[\.\!\?\n])\s+", (text or "").strip())
    return [x.strip() for x in raw if x and x.strip()]


def chunk_markdown_text(
    text: str,
    *,
    target_chars: int = 900,
    min_chars: int = 800,
    max_chars: int = 1000,
    overlap_chars: int = 120,
) -> list[dict]:
    """
    Chunk markdown into ~800-1000 chars.
    Keeps table/code blocks atomic and marks content_type.
    """
    text = (text or "").strip()
    if not text:
        return []

    # First pass by paragraphs to preserve markdown structures.
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p and p.strip()]
    chunks: list[dict] = []
    current = ""

    def flush_current():
        nonlocal current
        if current.strip():
            chunks.append({"content": current.strip(), "content_type": detect_content_type(current)})
            current = ""

    for p in paragraphs:
        p = p.strip()
        p_type = detect_content_type(p)
        # Keep tables/code as single units.
        if p_type in ("table", "code"):
            flush_current()
            chunks.append({"content": p, "content_type": p_type})
            continue

        # Text paragraphs: soft-pack by target size.
        if not current:
            current = p
            continue
        candidate = current + "\n\n" + p
        if len(candidate) <= max_chars:
            current = candidate
        else:
            flush_current()
            current = p
    flush_current()

    # Second pass: split oversized text chunks by sentence.
    normalized: list[dict] = []
    for c in chunks:
        c_text = c["content"]
        c_type = c["content_type"]
        if c_type != "text" or len(c_text) <= max_chars:
            normalized.append(c)
            continue

        sentences = _split_sentences(c_text)
        cur = ""
        for s in sentences:
            if not cur:
                cur = s
                continue
            maybe = f"{cur} {s}"
            if len(maybe) <= target_chars:
                cur = maybe
            else:
                normalized.append({"content": cur.strip(), "content_type": "text"})
                # small overlap for context continuity
                overlap = cur[-overlap_chars:] if overlap_chars > 0 else ""
                cur = (overlap + " " + s).strip() if overlap else s
        if cur.strip():
            normalized.append({"content": cur.strip(), "content_type": "text"})

    # Merge very small neighboring text chunks where possible.
    final: list[dict] = []
    for c in normalized:
        if (
            final
            and c["content_type"] == "text"
            and final[-1]["content_type"] == "text"
            and len(final[-1]["content"]) < min_chars
            and len(final[-1]["content"]) + 2 + len(c["content"]) <= max_chars
        ):
            final[-1]["content"] = final[-1]["content"] + "\n\n" + c["content"]
        else:
            final.append(dict(c))
    return final
