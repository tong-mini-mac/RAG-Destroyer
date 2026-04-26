from __future__ import annotations

from abc import ABC, abstractmethod


class KnowledgeSource(ABC):
    """Abstract knowledge source for vault-like markdown retrieval."""

    @abstractmethod
    def list_departments(self) -> list[str]:
        """Return top-level department names available in this source."""

    @abstractmethod
    def iter_markdown_files(self, department: str):
        """Yield absolute markdown file paths for one department."""

    @abstractmethod
    def cache_path(self) -> str:
        """Return cache json path for this source."""

    @abstractmethod
    def master_index_path(self) -> str:
        """Return master index markdown path for this source."""
