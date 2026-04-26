# SAG Runbook (V2/V3)

## 1) Startup

### Local

- `python -m pip install -r requirements.txt`
- `streamlit run app.py`

### Docker

- Copy `config/.env.example` to `config/.env`
- Create folders: `knowledge/`, `raw_data/`, `logs/`
- `docker compose up --build`

UI endpoint: `http://localhost:8501`

## 2) Health Checks

- Open UI and verify provider/API key readiness in `Start`.
- Confirm vault path exists and has markdown files.
- Confirm identity-scoped document preview shows expected files.
- Confirm query returns answer with source citations.

## 3) Rebuild Index / Cache

Use UI path:

- `System Config` -> `Rebuild vault index & search cache`

When to run:

- After bulk import under `knowledge/`
- After changing vault paths
- After role/silo reorganization

V3 note:

- Rebuild now also refreshes:
  - `_CHUNK_INDEX.json`
  - `_VECTOR_INDEX.json`

## 3.1) Retrieval Strategy Settings (V3)

Use UI path:

- `System Config` -> `Retrieval architecture`

Recommended production-safe setting:

- Enable hybrid retrieval
- Strategy: `dynamic_rerank`
- Vector index stage: OFF (unless intentionally testing vector-plus-rerank)

Env equivalents:

- `SAG_ENABLE_HYBRID=true`
- `SAG_HYBRID_STRATEGY=dynamic_rerank`
- `SAG_ENABLE_VECTOR_INDEX=false`
- `SAG_HYBRID_TOP_K=5`
- `SAG_HYBRID_ALPHA=0.65`

## 4) Incident Triage

### No results returned

- Confirm selected role/department has authorized files.
- Confirm file names and folder names match `config/org_structure.json`.
- Rebuild index/cache.
- Rephrase query with policy vocabulary used in documents.
- Review `config/domain_synonyms.json` and add missing domain synonyms.
- Check `logs/retrieval_trace.jsonl` for stage timings and `sources_count=0`.

### API/provider failures

- Verify key in session or `config/.env`.
- Check quota/rate limits.
- Check outbound network.
- Review logs and retry.

### Incorrect RBAC visibility

- Validate role mapping in `config/org_structure.json`.
- Validate denylist/cross-access config files.
- Validate YAML `audience` in markdown front matter.
- Verify role simulation + active department in the UI.
- Confirm no manual edits bypassed `document_visible_to_viewer`.

### Slow responses / latency spikes

- Inspect `logs/retrieval_trace.jsonl` for which stage is slow:
  - `keyword_gen`
  - `lexical_search`
  - `rerank`
  - `synthesis`
- If `lexical_search` dominates, rebuild index and confirm cache coverage.
- If `synthesis` dominates, check provider latency/quota/model size.
- If keyword stage fails often, tune `config/domain_synonyms.json`.

## 5) Recovery Basics

- Restart Streamlit process (or container).
- Rebuild vault index/cache.
- Re-run a known-good test query per role.

## 6) Operational Checklist

- Backup cadence for `knowledge/`, `config/`, `logs/`
- Secret rotation policy for API keys
- Access review for silo directories and deployment host
- Periodic review of `logs/retrieval_trace.jsonl` p50/p95 trends
- Keep `config/domain_synonyms.json` aligned with business vocabulary
