# Specification: Subtrack Phase 1 — Web App Shell & Navigation Layout

## 1. Goal
Initialize the modern web application architecture for StashStats. Set up the Dash application factory with Dash Bootstrap Components (`dbc.themes.DARKLY`), create the global top header with user profile badge and sync indicators, and assemble the main 4-tab container layout.

## 2. Scope & Components
- **Dependencies**: Add `dash`, `dash-bootstrap-components`, and `uvicorn` in `pyproject.toml`.
- **Application Factory (`src/stashstats/web/app.py`)**:
  - Initializes Dash app with `dbc.themes.DARKLY`.
  - Configures suppress_callback_exceptions=True for multi-tab rendering.
  - Exposes underlying ASGI / WSGI server for FastAPI / Uvicorn runner.
- **Global Header Component (`src/stashstats/web/components/header.py`)**:
  - App brand title ("StashStats").
  - Current authenticated user badge (`@username` from `RavelryClient.get_current_user()` or fallback).
  - Last synced timestamp and sync trigger button.
- **Main Layout Shell (`src/stashstats/web/layouts/main.py`)**:
  - Responsive container with DBC Darkly styling.
  - 4 navigation tabs: `Personal Stash` (default active), `Stash Analytics` (stub), `Projects` (stub), `Yarn Search` (stub).
  - Tab content wrapper container ready for child view injection.
- **Testing**:
  - `tests/web/test_app.py`: Validate application factory, theme stylesheet injection, and server exposure.
  - `tests/web/test_header.py`: Validate header component rendering, user badge, and tab structure.
