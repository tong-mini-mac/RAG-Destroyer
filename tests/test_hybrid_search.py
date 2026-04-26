from core.HybridSearch import HybridSearchEngine


def test_hybrid_rerank_merges_duplicates_and_limits_top_k():
    engine = HybridSearchEngine(alpha=0.7, top_k=2)
    search_results = [
        {
            "keyword": "policy",
            "hits": [
                {"path": "a.md", "title": "Travel Policy", "summary": "Allowance and travel claims", "tags": ["hr"], "relevance": 10},
                {"path": "b.md", "title": "Payroll Rules", "summary": "Monthly salary process", "tags": ["finance"], "relevance": 8},
            ],
        },
        {
            "keyword": "allowance",
            "hits": [
                {"path": "a.md", "title": "Travel Policy", "summary": "Allowance and travel claims", "tags": ["hr"], "relevance": 9},
            ],
        },
    ]

    out = engine.rerank("travel allowance policy", search_results)

    assert len(out) == 2
    assert out[0]["path"] == "a.md"
    assert out[0]["hit_count"] == 2
    assert "hybrid_score" in out[0]


def test_hybrid_rerank_handles_empty_input():
    engine = HybridSearchEngine()
    assert engine.rerank("anything", []) == []
