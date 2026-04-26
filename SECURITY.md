# Security Policy

## Scope

This repository is a proof-of-concept implementation of SAG (Subset-Augmented Generation). It is designed for deterministic retrieval and RBAC-aware filtering over Markdown knowledge silos.

## Reporting a Vulnerability

- Do not open public issues for suspected security vulnerabilities.
- Report privately to the maintainer through GitHub security reporting or direct contact.
- Include:
  - Affected files/components
  - Reproduction steps
  - Expected vs actual behavior
  - Impact assessment (confidentiality/integrity/availability)

## Security Expectations for Contributors

- Never commit `config/.env`, API keys, tokens, or secrets.
- Never commit private vault content from `knowledge/`, `raw_data/`, or sensitive logs.
- Preserve RBAC and audience filtering semantics when changing retrieval logic.
- Keep deterministic behavior auditable (clear reason why a source was included).

## Data Handling

- Public repository should contain code and docs only.
- `knowledge/` and `raw_data/` are treated as sensitive runtime data.
- Logs and audit artifacts should be reviewed before sharing outside controlled environments.

## Hardening Checklist (Recommended for Production Deployments)

- Enforce OS-level folder permissions for silo directories.
- Run behind TLS/reverse proxy if exposed beyond localhost.
- Store secrets in a dedicated secret manager.
- Enable alerting for repeated LLM/provider failures.
- Add periodic backup and restore verification for `knowledge/`, `config/`, and `logs/`.
