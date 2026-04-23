# SAG V2 Architecture (Deterministic + RBAC-first)

## Core flow

1. User selects identity context (role + active department when applicable).
2. Policy gate resolves authorized silo subset.
3. Deterministic retrieval scans authorized files using metadata and keyword strategy.
4. Best subset is assembled with relevance and hit intersections.
5. LLM synthesizes response from authorized subset only.
6. UI exposes source evidence and optional audit feedback.

## Main components

- `app.py`: Streamlit runtime and operator workflows.
- `core/Orchestrator.py`: query orchestration, keyword strategy, synthesis lifecycle.
- `core/SearchWorker.py`: deterministic per-keyword vault search.
- `core/Utils.py`: RBAC + per-file policy filters, config loading, utility guards.
- `core/VaultWarden.py`: vault indexing and cache refresh.
- `core/AuditJudge.py`: quality scoring and feedback loop.

## Security model

- Folder-scope authorization by role and department.
- Per-file policy controls via config allow/deny lists.
- Optional front matter audience restrictions (`all`, `management`).
- Deterministic inclusion path designed for auditability.

## Operational model

- Local and Docker runtime supported.
- Vault/index rebuild available via `System Config`.
- Notifications (LINE/Discord) for critical runtime failures.
