from core.Orchestrator import _expand_keywords_with_synonyms


def test_keyword_synonym_expansion_deduplicates_case_insensitive():
    synonyms = {
        "welfare": ["benefits", "allowance"],
        "benefits": ["Welfare", "insurance"],
    }
    out = _expand_keywords_with_synonyms(["welfare", "Benefits"], synonyms)
    assert out[0].lower() == "welfare"
    lowered = [x.lower() for x in out]
    assert "benefits" in lowered
    assert "allowance" in lowered
    assert "insurance" in lowered
    assert lowered.count("welfare") == 1
