# Plan: Log Usage History Table

**Goal:** Add a table showing past usage change events inside the "Log Usage" tab of the personal stash edit modal, underneath the save/cancel boxes.

---

### Task 1: Update Modal Layout

**Files:**
- Modify: [edit_modal.py](file:///home/thotsky/BrainVault/Projects/StashStats/stashies/components/edit_modal.py)

- [x] **Step 1: Add container div for usage history**
  Add a new `html.Div` element with ID `"edit-stash-history-table"` inside the `Log Usage` tab layout (Tab 2), below the remaining preview block.
  ```python
  html.Div(
      id="edit-stash-history-table",
      className="mt-3"
  )
  ```

---

### Task 2: Populate Table in Controller

**Files:**
- Modify: [app_controller.py](file:///home/thotsky/BrainVault/Projects/StashStats/stashies/app_controller.py)

- [x] **Step 1: Build table builder helper**
  Create a helper method `build_history_table(self, stash_id: str) -> html.Div` that:
  - Fetches events using `self.MODEL.get_stash_history(stash_id)`.
  - If no events, returns a simple message: `html.Div("No usage history logged yet.", className="text-muted small")`.
  - If events are found, builds a `dbc.Table` with headers: `Date`, `Skeins`, `Yards/Meters`, `Weight`.
  - Formats deltas (which are stored as negative values) as positive numbers for readability (e.g., `-1.5` skeins in DB is rendered as `1.5 skeins used`).

- [x] **Step 2: Update toggle_edit_modal return values**
  Modify `toggle_edit_modal` in `app_controller.py` to return the rendered history table layout (or empty div on cancel) as the 15th output value.

---

### Task 3: Wire Callbacks in app.py

**Files:**
- Modify: [app.py](file:///home/thotsky/BrainVault/Projects/StashStats/app.py)

- [x] **Step 1: Update toggle_edit_modal Callback**
  Add `Output("edit-stash-history-table", "children")` to the `toggle_edit_modal` callback outputs.
  Update the callback implementation to return the history table value returned by the controller.

- [x] **Step 2: Update save_stash_details Callback**
  Add `Output("edit-stash-history-table", "children", allow_duplicate=True)` to the save stash callback outputs.
  After saving a new usage event, call `CONTROLLER.build_history_table(stash_id)` and return it so the table refreshes dynamically.

---

### Task 4: Verification

- [x] **Step 1: Run E2E Tests**
  Run `pytest` to verify that existing modal open/close functionality is unaffected.
- [x] **Step 2: Manual Check**
  Open edit modal on personal stash card, switch to "Log Usage" tab, verify history table displays correctly with correct formatting.
