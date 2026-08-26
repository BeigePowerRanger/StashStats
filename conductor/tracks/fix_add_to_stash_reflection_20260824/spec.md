# Specification: Fix 'Add to Stash' Reflection in Personal Stash and Analytics

### 1. Overview
Ensure that when a user clicks "Add Yarn to Stash" on any search result in the Yarn Search tab, the item is created via the Ravelry API (if client authenticated) or synthesized locally, persisted into `stash-raw-store`, and immediately reflected across the Personal Stash inventory list and Stash Analytics charts.

### 2. Functional Requirements
- **`handle_add_to_stash_logic` Implementation (`callbacks/search.py`)**:
  - Receive submitted fields: `yarn_id`, `skeins`, `colorway`, `dyelot`, `location`, `notes`, `date_added`, `search_results`, and `raw_stash_items`.
  - If authenticated client is available, call `client.create_stash_item(...)`.
  - If offline/client unavailable, synthesize a valid `StashItem` dict with calculated yardage, weight, colorway, and status.
  - Prepend the created item into `stash-raw-store` data.
  - Return updated status message and updated `stash-raw-store` data.
- **Callback Wiring (`callbacks/search.py`)**:
  - Connect `Output("stash-raw-store", "data", allow_duplicate=True)` to `handle_add_to_stash`.
  - Pass `State("yarn-search-results-store", "data")` and `State("stash-raw-store", "data")`.

### 3. Acceptance Criteria
- Clicking "Add Yarn to Stash" adds the item to `stash-raw-store`.
- Personal Stash accordion and Stash Analytics immediately reflect the new yarn without requiring manual page reload.
- Unit tests verify client creation, store update, and reactive state changes.
- 100% automated test pass rate with coverage >80%.
