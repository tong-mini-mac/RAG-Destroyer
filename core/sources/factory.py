from __future__ import annotations

from .base import KnowledgeSource
from .localfs import LocalFSKnowledgeSource


def build_knowledge_source(backend: str, vault_path: str) -> KnowledgeSource:
    """
    Build the configured knowledge source provider.

    Current behavior is intentionally backward-compatible:
    - localfs (default): existing Obsidian/markdown-on-disk behavior
    - unknown backends: graceful fallback to localfs
    """
    normalized = (backend or "localfs").strip().lower()
    if normalized == "localfs":
        return LocalFSKnowledgeSource(vault_path)
    return LocalFSKnowledgeSource(vault_path)
