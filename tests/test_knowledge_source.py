from core.sources import LocalFSKnowledgeSource, build_knowledge_source


def test_localfs_source_lists_departments_and_markdown_files(tmp_path):
    vault = tmp_path / "knowledge"
    (vault / "General").mkdir(parents=True)
    (vault / "General" / "a.md").write_text("# a", encoding="utf-8")
    (vault / "General" / "_SEARCH_CACHE.md").write_text("ignore", encoding="utf-8")
    (vault / ".hidden").mkdir(parents=True)

    source = LocalFSKnowledgeSource(str(vault))

    assert source.list_departments() == ["General"]
    files = list(source.iter_markdown_files("General"))
    assert len(files) == 1
    assert files[0].endswith("a.md")


def test_unknown_backend_falls_back_to_localfs(tmp_path):
    source = build_knowledge_source("something-else", str(tmp_path))
    assert isinstance(source, LocalFSKnowledgeSource)
