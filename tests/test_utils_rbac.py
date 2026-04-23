import os

from core.Utils import (
    count_markdown_docs_under,
    maybe_seed_demo_vault,
    normalize_audience_raw,
    role_is_management_or_above,
    viewer_may_read_audience,
)


def test_count_markdown_docs_under_ignores_private_index_files(tmp_path):
    dept = tmp_path / "Risk"
    dept.mkdir()
    (dept / "a.md").write_text("# a", encoding="utf-8")
    (dept / "_SEARCH_CACHE.md").write_text("# cache", encoding="utf-8")
    (dept / "b.txt").write_text("nope", encoding="utf-8")

    assert count_markdown_docs_under(str(dept)) == 1


def test_maybe_seed_demo_vault_copies_markdown_when_empty(tmp_path):
    root = tmp_path / "repo"
    vault = tmp_path / "knowledge"
    demo = root / "demo_knowledge" / "General"
    demo.mkdir(parents=True)
    (demo / "policy.md").write_text("# policy", encoding="utf-8")

    copied = maybe_seed_demo_vault(str(root), str(vault))

    assert copied is True
    assert os.path.isfile(vault / "General" / "policy.md")


def test_maybe_seed_demo_vault_skips_when_opt_out_file_exists(tmp_path):
    root = tmp_path / "repo"
    vault = tmp_path / "knowledge"
    demo = root / "demo_knowledge" / "General"
    demo.mkdir(parents=True)
    vault.mkdir(parents=True)
    (demo / "policy.md").write_text("# policy", encoding="utf-8")
    (vault / ".no_auto_demo").write_text("", encoding="utf-8")

    copied = maybe_seed_demo_vault(str(root), str(vault))

    assert copied is False
    assert not os.path.isfile(vault / "General" / "policy.md")


def test_management_audience_rules():
    assert normalize_audience_raw("management") == "management"
    assert normalize_audience_raw("public") == "all"
    assert role_is_management_or_above("CEO")
    assert role_is_management_or_above("Department Head")
    assert not role_is_management_or_above("Operational Staff")
    assert viewer_may_read_audience("Department Head", "management")
    assert not viewer_may_read_audience("Operational Staff", "management")
