# Contributing to SAG

## Development Principles

- Keep retrieval deterministic and explainable.
- Preserve RBAC-first behavior.
- Prefer simple, testable changes over broad rewrites.
- Keep documentation aligned with actual behavior.

## Local Setup

1. Create a virtual environment.
2. Install dependencies:
   - `python -m pip install -r requirements.txt`
   - `python -m pip install pytest`
3. Run tests:
   - `pytest`
4. Run app:
   - `streamlit run app.py`

## Pull Request Guidelines

- Scope PRs to one focused change.
- Include:
  - Why the change is needed
  - User impact
  - Test evidence
- Update docs when behavior changes.
- Avoid unrelated formatting-only diffs.

## Code Quality Checklist

- [ ] No secrets committed
- [ ] RBAC/audience checks preserved
- [ ] Tests added or updated
- [ ] README/docs updated (if relevant)
- [ ] No large binary artifacts unless required

## Recommended Areas for Contributions

- RBAC test coverage
- Deterministic search performance
- Operational reliability (monitoring, runbooks, recovery)
- Documentation clarity for evaluators and enterprise teams
