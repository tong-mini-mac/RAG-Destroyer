# SAG V2 Runbook

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

## 4) Incident Triage

### No results returned

- Confirm selected role/department has authorized files.
- Confirm file names and folder names match `config/org_structure.json`.
- Rebuild index/cache.
- Rephrase query with policy vocabulary used in documents.

### API/provider failures

- Verify key in session or `config/.env`.
- Check quota/rate limits.
- Check outbound network.
- Review logs and retry.

### Incorrect RBAC visibility

- Validate role mapping in `config/org_structure.json`.
- Validate denylist/cross-access config files.
- Validate YAML `audience` in markdown front matter.

## 5) Recovery Basics

- Restart Streamlit process (or container).
- Rebuild vault index/cache.
- Re-run a known-good test query per role.

## 6) Operational Checklist

- Backup cadence for `knowledge/`, `config/`, `logs/`
- Secret rotation policy for API keys
- Access review for silo directories and deployment host
