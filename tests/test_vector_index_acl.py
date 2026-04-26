import os

from core.VectorIndex import VectorIndex


def test_vector_index_skips_table_and_enforces_acl(tmp_path):
    vault = tmp_path / "knowledge"
    dept = vault / "HR & Admin"
    dept.mkdir(parents=True)

    md = (
        "---\n"
        "title: HR Pay Policy\n"
        "doc_id: HRA-001\n"
        "tags: [hr, payroll]\n"
        "summary: payroll and allowance policy\n"
        "audience: management\n"
        "---\n\n"
        "This policy describes payroll and annual bonus in detail.\n\n"
        "| Item | Amount |\n"
        "|---|---|\n"
        "| Bonus | 10% |\n"
    )
    (dept / "policy.md").write_text(md, encoding="utf-8")

    ix = VectorIndex(str(vault))
    chunk_count, vector_count = ix.build()
    assert chunk_count >= 2
    assert vector_count >= 1

    # Operational staff should not see management content via parent ACL inheritance.
    no_hits = ix.query(
        "bonus payroll",
        allowed_subsets=["HR & Admin"],
        viewer_role="Operational Staff",
        viewer_active_department="HR & Admin",
    )
    assert no_hits == []

    # Department Head may see it.
    yes_hits = ix.query(
        "bonus payroll",
        allowed_subsets=["HR & Admin"],
        viewer_role="Department Head",
        viewer_active_department="HR & Admin",
    )
    assert yes_hits
    assert yes_hits[0]["doc_id"] == "HRA-001"
    assert os.path.basename(yes_hits[0]["path"]) == "policy.md"
