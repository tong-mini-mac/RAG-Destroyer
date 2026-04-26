from core.SearchWorker import SearchWorker


def test_cache_all_scope_uses_ratio_and_not_stale_when_coverage_high(monkeypatch):
    worker = SearchWorker("knowledge")
    monkeypatch.setattr(worker, "_total_md_in_vault_departments", lambda: 4)
    cache_data = {"General": [1, 2, 3, 4]}
    assert worker._cache_is_stale(cache_data, "ALL") is False


def test_cache_all_scope_marks_stale_when_coverage_low(monkeypatch):
    worker = SearchWorker("knowledge")
    monkeypatch.setattr(worker, "_total_md_in_vault_departments", lambda: 10)
    cache_data = {"General": [1, 2]}
    assert worker._cache_is_stale(cache_data, "ALL") is True
