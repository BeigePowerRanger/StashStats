# Implementation Plan: Dev/Prod Account Toggle (Runtime Auth Switcher)

## Phase 1: Settings & AccountManager (TDD)

- [ ] Task: Write failing unit tests for Settings credential pair fields
- [x] Task: Write failing unit tests for Settings credential pair fields [eb5ba25]
  - [x] Test `Settings` exposes `dev_username`, `dev_api_key`, `prod_username`, `prod_api_key` from env vars
  - [x] Test `Settings.auth_tuple_for(label)` returns correct (username, key) pair for `'dev'` and `'prod'`
- [x] Task: Update `Settings` in `src/stashstats/config.py` [eb5ba25]
  - [x] Add explicit `dev_username`, `dev_api_key`, `prod_username`, `prod_api_key` fields
  - [x] Add `auth_tuple_for(label: str) -> tuple[str, str]` method
  - [x] Keep existing `access_key` / `personal_key` for backward compatibility
- [~] Task: Write failing unit tests for `AccountManager`
  - [ ] Test default active label is `'dev'` on init
  - [ ] Test `get_active_label()` returns `'dev'` or `'prod'`
  - [ ] Test `switch()` toggles the active label
  - [ ] Test `get_client()` returns a `RavelryClient` instance
  - [ ] Test `get_active_username()` returns the resolved display name
  - [ ] Test error handling when credentials are missing/invalid
- [ ] Task: Implement `AccountManager` in `src/stashstats/auth.py`
  - [ ] Module-level singleton pattern (instance created at import time with `'dev'` default)
  - [ ] `switch()`: re-creates `RavelryClient` with new credential pair, calls `get_current_user()` to resolve display name
  - [ ] `get_client()`, `get_active_label()`, `get_active_username()` accessors
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Header Badge & Account Switch Modal UI (TDD)

- [ ] Task: Write failing unit tests for updated header component
  - [ ] Test `create_header()` renders a `dbc.Button` for the user badge (not just a `dbc.Badge`)
  - [ ] Test header renders a `DEV` or `PROD` env pill based on `active_label` param
  - [ ] Test badge text shows `@<username>` from active account
- [ ] Task: Update `src/stashstats/web/components/header.py`
  - [ ] Add `active_label: str = 'dev'` parameter to `create_header()`
  - [ ] Render `header-user-badge` as `dbc.Button` wrapping badge + env pill
  - [ ] Add `header-env-pill` span (`DEV` in warning color, `PROD` in danger color)
- [ ] Task: Write failing unit tests for `create_account_switch_modal()`
  - [ ] Test modal renders with correct id `account-switch-modal`
  - [ ] Test modal contains confirm and cancel buttons with correct ids
- [ ] Task: Implement `create_account_switch_modal()` in `src/stashstats/web/components/account_modal.py`
  - [ ] `dbc.Modal` with dynamic body message, Confirm and Cancel buttons
- [ ] Task: Update `src/stashstats/web/layouts/main.py` to include the account switch modal
- [ ] Task: Update `src/stashstats/web/app.py` to pass `active_label` and `username` from `AccountManager` to `create_main_layout()`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Switch Callback & Full Data Reload (TDD)

- [ ] Task: Write failing unit tests for account switch callback logic
  - [ ] Test confirm button triggers account switch via `AccountManager.switch()`
  - [ ] Test data stores are updated with new account's stash and projects
  - [ ] Test header badge and env pill text update after switch
  - [ ] Test cancel button closes modal without switching
  - [ ] Test error case: switch fails → error badge shown, stores unchanged
- [ ] Task: Implement `register_auth_callbacks()` in `src/stashstats/web/callbacks/auth.py`
  - [ ] Callback: `account-switch-confirm-btn` click → `AccountManager.switch()`, re-fetch stash + projects, update stores, update header outputs, close modal
  - [ ] Callback: `account-switch-cancel-btn` click → close modal, no state change
  - [ ] Add `Output` for `header-user-badge` children, `header-env-pill` children, modal `is_open`
- [ ] Task: Register `register_auth_callbacks()` in `src/stashstats/web/app.py`
- [ ] Task: Full test run + coverage verification (>80%)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
