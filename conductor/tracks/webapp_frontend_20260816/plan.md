# Implementation Plan: Web App Frontend — Core Shell & Personal Stash

## Task 1: Dependencies & Application Factory (TDD)
- [x] Subtask 1.1: Add `dash`, `dash-bootstrap-components`, and `uvicorn` in `pyproject.toml` and sync environment via `uv sync`.
- [x] Subtask 1.2: Write tests in `tests/web/test_app.py` verifying Dash app creation, Darkly theme configuration, and server exposure.
- [x] Subtask 1.3: Implement `create_app()` factory in `src/stashstats/web/app.py`.
- [x] Subtask 1.4: Run `pytest tests/web/test_app.py` and ensure passing.

## Task 2: Global Header & Navigation Shell (TDD)
- [x] Subtask 2.1: Write tests in `tests/web/test_header.py` for branding, `@username` badge, sync indicator, and 4-tab container structure.
- [x] Subtask 2.2: Implement `src/stashstats/web/components/header.py` and `src/stashstats/web/layouts/main.py`.
- [x] Subtask 2.3: Run `pytest tests/web/test_header.py` and ensure passing.

## Task 3: Personal Stash Grouped Accordion View (TDD)
- [x] Subtask 3.1: Write tests for parent-yarn grouping engine, sorting, and filtering in `tests/web/test_stash_view.py`.
- [x] Subtask 3.2: Implement grouping logic and grouped accordion card components in `src/stashstats/web/components/stash.py`.
- [x] Subtask 3.3: Implement search filter, sort dropdown, and pagination in `src/stashstats/web/layouts/stash.py`.
- [x] Subtask 3.4: Add reactive callbacks for interactions in `src/stashstats/web/callbacks/stash.py`.

## Task 4: Stash Edit & Usage Modal Dialog (TDD)
- [x] Subtask 4.1: Write tests for the modal dialog states and proportional math in `tests/web/test_modal.py`.
- [x] Subtask 4.2: Implement the two-tab interactive modal dialog in `src/stashstats/web/components/modal.py`.
- [x] Subtask 4.3: Implement reactive callbacks for modal interactions and history ledger rollback in `src/stashstats/web/callbacks/modal.py`.

## Task 5: Integration & Local Verification
- [x] Subtask 5.1: Write end-to-end integration tests for the full web application.
- [x] Subtask 5.2: Create a CLI entry point launcher for the web app in `src/stashstats/cli.py` or similar.
- [x] Subtask 5.3: Run `ruff check .` and `pytest` to verify all components work together.

## Phase: Review Fixes
- [x] Task: Apply review suggestions 06bc250
