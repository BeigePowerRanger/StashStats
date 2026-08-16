# Implementation Plan: Subtrack Phase 1 — Web App Shell & Navigation Layout

## Task 1: Dependencies & Application Factory (TDD)
- [ ] Subtask 1.1: Add `dash`, `dash-bootstrap-components`, and `uvicorn` in `pyproject.toml` and sync environment via `uv sync`.
- [ ] Subtask 1.2: Write tests in `tests/web/test_app.py` verifying Dash app creation, Darkly theme configuration, and server exposure.
- [ ] Subtask 1.3: Implement `create_app()` factory in `src/stashstats/web/app.py`.
- [ ] Subtask 1.4: Run `pytest tests/web/test_app.py` and ensure passing.

## Task 2: Global Header & Navigation Shell (TDD)
- [ ] Subtask 2.1: Write tests in `tests/web/test_header.py` for branding, `@username` badge, sync indicator, and 4-tab container structure.
- [ ] Subtask 2.2: Implement `src/stashstats/web/components/header.py` and `src/stashstats/web/layouts/main.py`.
- [ ] Subtask 2.3: Run `pytest tests/web/test_header.py` and ensure passing.

## Task 3: Quality Check & Phase 1 Checkpoint
- [ ] Subtask 3.1: Run `ruff check .` and `pytest`.
- [ ] Subtask 3.2: Mark Phase 1 subtrack complete in `index.md` and parent track `plan.md`.
- [ ] Subtask 3.3: Scaffold Phase 2 subtrack (`phase2_stash_accordion`).
