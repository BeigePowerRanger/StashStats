# Specification: Dev/Prod Account Toggle (Runtime Auth Switcher)

## Overview

Add a runtime-safe mechanism to switch between two Ravelry API accounts (Dev and Prod) using the existing header badge. The app always boots into the Dev account. Clicking the `@username` badge in the header opens a confirmation modal to toggle accounts, triggering a full in-page data reload. No credentials are hardcoded; both account pairs come from the existing `.env` file (`DEV_USERNAME`/`DEV_API_KEY` and `PROD_USERNAME`/`PROD_API_KEY`).

## Functional Requirements

1. **Settings**: `Settings` is extended to expose both Dev and Prod credential pairs explicitly as named fields (`dev_username`, `dev_api_key`, `prod_username`, `prod_api_key`).

2. **AccountManager**: A module-level singleton (`src/stashstats/auth.py`) tracks:
   - The currently active account label (`'dev'` or `'prod'`), defaulting to `'dev'` on startup.
   - The currently active `RavelryClient` instance.
   - Methods: `switch()`, `get_client()`, `get_active_label()`, `get_active_username()`.

3. **RavelryClient re-initialization**: On account switch, `AccountManager.switch()` re-creates a `RavelryClient` with the new credential pair and resolves the Ravelry display name via `get_current_user()`.

4. **Header Badge**: The `@username` badge in the global header:
   - Shows `@<ravelry_display_name>` + a small `DEV` or `PROD` environment pill beside it.
   - The badge is rendered as a clickable `dbc.Button` (id: `"header-user-badge"`) that opens the switch modal.

5. **Account Switch Modal** (`id: "account-switch-modal"`):
   - Content: *"Switch to [other_label] account (@other_display_name)? All currently displayed data will reload."*
   - Buttons: **Confirm** (`id: "account-switch-confirm-btn"`) and **Cancel** (`id: "account-switch-cancel-btn"`).

6. **Switch Callback**: A Dash callback wired to the Confirm button:
   - Calls `AccountManager.switch()` to toggle active account and re-initialize the client.
   - Re-fetches stash data and projects data for the new account.
   - Updates `stash-raw-store`, `projects-raw-store`, header badge text, env pill, and modal open state.
   - On error: surfaces a visible error badge on the header and aborts data update.

7. **No persistence**: Active account is runtime-only; server restart always returns to `'dev'`.

## Non-Functional Requirements

- Switch must not crash the server; all errors surface as a visible error badge/toast.
- No breaking changes to existing callback signatures or component IDs (except `header-user-badge` becoming a `dbc.Button`).
- All new code follows project type hint and docstring standards.

## Acceptance Criteria

- [ ] App starts as DEV; header shows DEV account display name + `DEV` env pill.
- [ ] Clicking badge opens confirmation modal correctly identifying the target account name.
- [ ] Confirming switch: header badge and env pill update; all data stores reload with the new account's data.
- [ ] Cancelling modal: no state change.
- [ ] Server restart: always returns to DEV account.
- [ ] All new and modified modules have unit tests; overall coverage >80%.

## Out of Scope

- OAuth / browser-based Ravelry login flow.
- More than two accounts.
- Persisting active account to disk across server restarts.
- Per-user session isolation (single-user app assumed).
