from __future__ import annotations

import os

from .base import KnowledgeSource


class LocalFSKnowledgeSource(KnowledgeSource):
    """Default local markdown vault provider (Obsidian-compatible)."""

    def __init__(self, vault_path: str):
        self.vault_path = vault_path

    def list_departments(self) -> list[str]:
        if not os.path.isdir(self.vault_path):
            return []
        out = []
        for name in os.listdir(self.vault_path):
            if name.startswith("_") or name.startswith("."):
                continue
            full_path = os.path.join(self.vault_path, name)
            if os.path.isdir(full_path):
                out.append(name)
        return sorted(out)

    def iter_markdown_files(self, department: str):
        base = os.path.join(self.vault_path, department)
        if not os.path.isdir(base):
            return
        for root, _, files in os.walk(base):
            for fname in files:
                if fname.endswith(".md") and not fname.startswith("_"):
                    yield os.path.join(root, fname)

    def cache_path(self) -> str:
        return os.path.join(self.vault_path, "_SEARCH_CACHE.json")

    def master_index_path(self) -> str:
        return os.path.join(self.vault_path, "_MASTER_INDEX.md")
