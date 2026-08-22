# StashStats User Problem Discoveries

Log of user-reported issues, root cause isolations, and impacted components.

---

## Template

### [DISC-XXX] <Short Title>
- **Date Reported:** YYYY-MM-DD
- **Observed Behavior:** <What user experienced>
- **Location / Components:**
  - Files: `path/to/file.py:line`
  - Routes / UI: `<route>` or `<tab>`
- **Root Cause Analysis:** <Why it happens>
- **Status:** `Investigating` | `Isolated` | `Fixed` | `Track Created`
- **Related Track / Issue:** <link or track id>

---

### [DISC-001] Missing Weight in Ounces (oz) on Yarn Search Results
- **Date Reported:** 2026-08-18
- **Observed Behavior:** Yarn search results do not display skein weight in ounces (`oz`).
- **Location / Components:**
  - Files: [`src/stashstats/web/components/search.py:154-160`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/web/components/search.py#L154-L160)
  - Routes / UI: Yarn Search Tab (`create_yarn_search_details`)
- **Root Cause Analysis:**
  1. `create_yarn_search_details` branches mutually exclusively on `if yarn.yarn_weight and yarn.yarn_weight.name:` vs `elif grams is not None:`. If a yarn has a weight category (e.g., "Worsted", "DK"), `grams` is completely omitted from the specs list.
  2. When `grams` is rendered, only metric grams (`{grams}g`) is formatted. No conversion to ounces (`grams / 28.34952` -> `oz`) is performed or shown (e.g., `100g / 3.53 oz`).
  3. Search query filters do not support oz/weight filtering.
- **Proposed Solution:**
  - In [`src/stashstats/web/components/search.py`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/web/components/search.py), display yarn weight category (e.g., `Weight Category: Worsted`) and physical skein weight (`Weight: 100g (3.53 oz)`) independently.
  - Calculate `oz = grams / 28.34952` and format as dual unit (`{grams:g}g ({oz:.2f} oz)` or `{oz:.2f} oz / {grams:g}g`).
- **Status:** `Isolated`
- **Related Track / Issue:** None

---

### [DISC-002] "Add Yarn to Stash" from Yarn Search Does Not Create or Persist Stash Item
- **Date Reported:** 2026-08-18
- **Observed Behavior:** Submitting the inline "Add Yarn to Stash" form on a yarn search result does not convert the yarn into a stash item or persist it to the user's stash.
- **Location / Components:**
  - Files:
    - [`src/stashstats/web/callbacks/search.py:284-311`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/web/callbacks/search.py#L284-L311) (`handle_add_to_stash` callback)
    - [`src/stashstats/web/components/search.py:208-336`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/web/components/search.py#L208-L336) (`create_yarn_search_details` inline stash form)
    - [`src/stashstats/client.py:207-265`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/client.py#L207-L265) (`create_stash_item`)
  - Routes / UI: Yarn Search Tab (Accordion item -> "Add Yarn to Stash" form)
- **Root Cause Analysis:**
  1. `handle_add_to_stash` in `src/stashstats/web/callbacks/search.py` is a UI mock/stub. It only generates a formatted string message (`"Successfully added {skein_str} (Yarn #{yarn_id}) to stash!"`) and does not execute any backend logic.
  2. It does not invoke `client.create_stash_item()` or create a `StashItem` model.
  3. It does not output or append to `stash-raw-store` (the Dash store powering the Personal Stash tab), leaving the in-app stash item list unchanged.
  4. The form lacks access to the parent yarn object's metadata (yardage per skein, grams per skein) needed to calculate `total_grams` and `total_yards` when creating the stash entry.
- **Proposed Solution:**
  - Update `handle_add_to_stash` to call `client.create_stash_item()` if an authenticated client is present.
  - In offline / mock mode or upon successful API response, construct a `StashItem` dictionary with calculated totals (`total_grams = skeins * grams_per_skein`, `total_yards = skeins * yards_per_skein`) and append it to `stash-raw-store` via Dash callback `Output("stash-raw-store", "data", allow_duplicate=True)`.
- **Status:** `Isolated`
- **Related Track / Issue:** None

---

### [DISC-003] "Date Added" Input Field Unreadable in Dark Theme (Yarn Search Form)
- **Date Reported:** 2026-08-18
- **Observed Behavior:** The "Date Added" input field in the search tab's "Add to Stash" form is visually unreadable due to low contrast / unstyled white background in dark mode.
- **Location / Components:**
  - Files:
    - [`src/stashstats/web/components/search.py:305-314`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/web/components/search.py#L305-L314) (`dcc.DatePickerSingle`)
    - [`assets/custom.css`](file:///home/thotsky/CodeVault/StashStats/assets/custom.css) (missing dark theme styles for `dcc.DatePickerSingle`)
  - Routes / UI: Yarn Search Tab (Accordion item -> "Add to Stash" form -> "Date Added")
- **Root Cause Analysis:**
  1. `src/stashstats/web/components/search.py` embeds `dcc.DatePickerSingle` directly inside a `#222` dark background container without styling overrides.
  2. `dcc.DatePickerSingle` relies on `react-dates`, which renders with hardcoded light theme colors (white input boxes, light gray text/borders) that collide with dark Bootstrap themes, producing illegible white-on-white or dark-on-dark text contrast.
  3. Other parts of the application (e.g. `src/stashstats/web/components/modal.py:628-633`) use standard HTML5 `dbc.Input(type="date", ...)` with `DARK_INPUT_STYLE` / `className="bg-dark text-light border-secondary"`, which seamlessly adheres to the dark theme.
- **Proposed Solution:**
  - Replace `dcc.DatePickerSingle` in [`src/stashstats/web/components/search.py`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/web/components/search.py) with `dbc.Input(type="date", id={"type": "stash-date-added", "index": yarn_id}, value=datetime.now(tz=UTC).date().isoformat(), style=DARK_INPUT_STYLE)`.
  - Update `handle_add_to_stash` in [`src/stashstats/web/callbacks/search.py`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/web/callbacks/search.py) from `State({"type": "stash-date-added", ...}, "date")` to `State({"type": "stash-date-added", ...}, "value")`.
- **Status:** `Isolated`
- **Related Track / Issue:** None

---

### [DISC-004] Missing Manual Stash Add Functionality (Weight in g/oz, Yardage, Colorway, Yarn Name)
- **Date Reported:** 2026-08-18
- **Observed Behavior:** No UI or workflow exists to manually create or add a custom stash yarn with user-specified weight (grams/oz), yardage, colorway, brand, and yarn name without searching the Ravelry catalog.
- **Location / Components:**
  - Files:
    - [`src/stashstats/web/layouts/stash.py:50-98`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/web/layouts/stash.py#L50-L98) (Personal Stash toolbar / header)
    - [`src/stashstats/web/components/modal.py`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/web/components/modal.py) (Stash edit modal - only edits existing items)
    - [`src/stashstats/models/stash.py:18-72`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/models/stash.py#L18-L72) (`Pack` & `StashItem` models)
    - [`src/stashstats/client.py:207-265`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/client.py#L207-L265) (`create_stash_item`)
  - Routes / UI: Personal Stash Tab & Yarn Search Tab
- **Root Cause Analysis:**
  1. The Personal Stash tab only has a "Sync Now" button and search/filter inputs; it lacks an "Add Custom Yarn" / "Manual Add" entrypoint.
  2. The only yarn addition path currently is the search accordion inline form, which strictly requires choosing a catalog search result and does not expose fields for `yarn_name`, `yarn_company_name`, `weight_grams`, `weight_oz`, or `yardage`.
  3. The underlying `Pack` model already includes `total_grams`, `total_ounces`, `grams_per_skein`, `ounces_per_skein`, `total_yards`, `yards_per_skein`, and `colorway`, but there is no UI form exposing these fields for direct input or automatic two-way conversion (`g <-> oz`).
- **Proposed Solution:**
  - Add an "+ Add Custom Yarn" button to the Personal Stash action bar.
  - Create a "Manual Add Yarn" modal or form containing inputs for:
    - Yarn Line / Name (required)
    - Brand / Dyer Company (optional)
    - Colorway Name & Dye Lot
    - Skeins count
    - Weight per skein in Grams (g) with live-calculated / synchronized Ounces (oz) input (`1 oz = 28.34952 g`)
    - Yardage per skein
    - Location & Notes
  - Connect submission callback to build the `StashItem` and append to `stash-raw-store` (and sync via `client.create_stash_item()` if authenticated).
- **Status:** `Isolated`
- **Related Track / Issue:** None

---

### [DISC-005] Usage History Discoverability & Accessibility Issues
- **Date Reported:** 2026-08-18
- **Observed Behavior:** Usage history is difficult to find and inaccessible without clicking through multiple nested layers of the UI.
- **Location / Components:**
  - Files:
    - [`src/stashstats/web/components/stash.py:401-412`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/web/components/stash.py#L401-L412) (`create_stash_item_row` actions)
    - [`src/stashstats/web/components/modal.py:640-670`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/web/components/modal.py#L640-L670) (`create_stash_modal` layout)
    - [`src/stashstats/web/layouts/main.py:73-92`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/web/layouts/main.py#L73-L92) (Stash Analytics / global tabs)
  - Routes / UI: Personal Stash Tab -> Expand Accordion -> Click "Edit" -> Click "Log Usage" Tab -> Scroll to bottom
- **Root Cause Analysis:**
  1. Usage history is buried 4 layers deep: Personal Stash Tab -> Parent Accordion -> Stash Item Row -> "Edit" Button -> Modal -> "Log Usage" sub-tab -> Scroll past usage inputs.
  2. Stash item rows only expose a generic "Edit" button, offering no direct "History" / "Log Usage" action or badge showing how many usage entries exist.
  3. No aggregate or global usage log exists across the entire stash (e.g. in Stash Analytics or a dedicated Recent Activity section), making it impossible to see overall yarn consumption history in one place.
- **Proposed Solution:**
  - Add a dedicated "History" / "Log Usage" shortcut button directly on each stash item row in [`src/stashstats/web/components/stash.py`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/web/components/stash.py) to open the modal directly to the usage tab.
  - Show a small usage badge on rows that have logged history (e.g. `2 uses logged`).
  - Add an aggregated "Recent Stash Activity & Usage History" table/card in the Stash tab or Stash Analytics view aggregating history entries across all stash items.
- **Status:** `Isolated`
- **Related Track / Issue:** None

---

### [DISC-006] Usage History Not Immediately Available / Eagerly Loaded
- **Date Reported:** 2026-08-18
- **Observed Behavior:** Usage history is not immediately visible or preloaded; users must wait for on-demand modal fetch per item.
- **Location / Components:**
  - Files:
    - [`src/stashstats/web/callbacks/modal.py:334-342`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/web/callbacks/modal.py#L334-L342) (`handle_open_modal` lazy fetch)
    - [`src/stashstats/web/components/stash.py:287-415`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/web/components/stash.py#L287-L415) (`create_stash_item_row` lacks inline usage view)
    - [`src/stashstats/client.py:451-480`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/client.py#L451-L480) (`get_batch_stash_history`)
  - Routes / UI: Personal Stash Tab & Item Rows
- **Root Cause Analysis:**
  1. Usage history is only retrieved lazily when an item's modal is opened (`client.get_stash_history(stash_id)`), creating a delay and isolating history behind modal clicks.
  2. Batch history fetching (`client.get_batch_stash_history`) is never invoked during initial stash load or sync, so client stores (`stash-raw-store`) contain zero history metadata.
  3. Stash item rows and parent yarn accordions do not render recent usage records inline, requiring a modal interaction just to inspect past deductions.
- **Proposed Solution:**
  - Eagerly batch-fetch stash history during stash sync / load and embed in client store or dedicated `stash-history-store`.
  - Display the most recent usage snapshot directly on the expanded stash item row (e.g. inline collapsible history snippet: "Last used: 1.5 sk on 2026-08-01 for Sweater").
  - Provide a 1-click "History" quick drawer/table on the main Stash tab.
- **Status:** `Isolated`
- **Related Track / Issue:** None

---

### [DISC-007] Missing Project Association in Usage History Logging
- **Date Reported:** 2026-08-18
- **Observed Behavior:** When logging skein usage, there is no option/input to specify or link what project the yarn was used in.
- **Location / Components:**
  - Files:
    - [`src/stashstats/web/components/modal.py:603-662`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/web/components/modal.py#L603-L662) (`tab-log-usage` layout)
    - [`src/stashstats/web/components/modal.py:340-406`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/web/components/modal.py#L340-L406) (`create_usage_history_table`)
    - [`src/stashstats/models/history.py:6-57`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/models/history.py#L6-L57) (`StashHistoryEntry` model)
    - [`src/stashstats/web/callbacks/modal.py:119-179`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/web/callbacks/modal.py#L119-L179) (`handle_save_modal` callback)
  - Routes / UI: Stash Edit Modal -> "Log Usage" Tab & History Ledger Table
- **Root Cause Analysis:**
  1. The "Log Usage" form in [`src/stashstats/web/components/modal.py`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/web/components/modal.py) only contains `Skeins Used` and `Date Used` fields. It has no input or dropdown to associate the deduction with a project.
  2. [`src/stashstats/models/history.py`](file:///home/thotsky/CodeVault/StashStats/src/stashstats/models/history.py) (`StashHistoryEntry`) only has generic `notes: str | None`, lacking explicit schema fields for `project_name` / `project_id` / `project_url`.
  3. `create_usage_history_table` renders columns for Date, Skeins, Yards, Weight, and Action, but does not display which project or note the yarn was consumed for.
- **Proposed Solution:**
  - Add `project_name: str | None = None` and `project_id: int | None = None` to `StashHistoryEntry`.
  - Add a "Project Used In" input field (or user project dropdown if authenticated) in the "Log Usage" modal tab.
  - Update `handle_save_modal` to capture `project_name` and pass it to `apply_usage_to_stash` and `StashHistoryEntry`.
  - Add a "Project / Notes" column to `create_usage_history_table` to clearly display project associations.
- **Status:** `Isolated`
- **Related Track / Issue:** None







