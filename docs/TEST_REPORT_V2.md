# SAG V2 Test Report

Date: 2026-04-23  
Environment: Windows 10 (PowerShell), Python 3.13.12, Docker Compose v2

## Scope

- Validate V2 documentation and architecture updates
- Validate pluggable knowledge source integration (`localfs` default)
- Validate test, syntax, dependency, and Docker runtime readiness

## Results

### 1) Unit Tests (Detailed)

- Command: `pytest -vv`
- Result: PASS
- Output summary: `6 passed in 0.13s`

### 2) Syntax/Compile Smoke

- Command: `python -m compileall app.py core tests`
- Result: PASS
- Notes: All target modules compiled without syntax errors.

### 3) Dependency Consistency

- Command: `python -m pip check`
- Result: PASS
- Output summary: `No broken requirements found.`

### 4) Docker Compose Config Validation

- Command: `docker compose config`
- Result: PASS
- Notes: Compose file rendered successfully with expected binds and envs.

### 5) Docker Runtime Smoke

- Command: `docker compose up --build -d`
- Result: PASS
- Runtime check: `docker compose ps` reported `Up ... (healthy)` and port `8501` exposed.
- Logs check: `docker compose logs --no-color --tail 80` showed Streamlit startup and URLs.
- Teardown: `docker compose down` completed successfully.

## Not Covered

- End-to-end UI scenario automation (manual interactive flow only)
- External provider live API assertions (depends on user-provided credentials/quota)

## Conclusion

V2 changes are stable under local test conditions, Docker startup works, and the new source abstraction preserves default `localfs` behavior.
