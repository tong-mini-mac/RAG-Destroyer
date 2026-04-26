from core.Chunking import chunk_markdown_text, detect_content_type


def test_detect_content_type_table_and_code():
    table_md = "| Name | Value |\n|---|---|\n| A | 1 |"
    code_md = "```python\nprint('x')\n```"
    text_md = "Company policy for employee benefits."

    assert detect_content_type(table_md) == "table"
    assert detect_content_type(code_md) == "code"
    assert detect_content_type(text_md) == "text"


def test_chunking_keeps_table_chunk_and_text_chunk():
    src = (
        "This is an introduction paragraph about policy and compensation.\n\n"
        "| Name | Value |\n|---|---|\n| Allowance | 1000 |\n\n"
        "Final notes for operations."
    )
    out = chunk_markdown_text(src, target_chars=200, min_chars=80, max_chars=260, overlap_chars=20)
    assert out
    types = [x["content_type"] for x in out]
    assert "table" in types
    assert "text" in types
