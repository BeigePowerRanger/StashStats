# Resolve Warnings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Address warnings and minor issues from StashStats.md.

**Architecture:** We will systematically resolve specific warnings in app.py, app_controller.py, yarn.py, and projects.py to improve code quality, safety, and reliability.

**Tech Stack:** Python, pytest

---

### Task 1: Fix dynamic modal trigger and unused category filter

**Files:**
- Modify: `app.py`

- [x] **Step 1: Check edit_clicks positive values in toggle_edit_modal**
  Modify the `toggle_edit_modal` callback in `app.py` to prevent execution if it is triggered by dynamic render instead of an actual click.
  Code change:
  ```python
  def toggle_edit_modal(edit_clicks, cancel_click, store_data_list, btn_ids):
      ctx = callback_context
      if not ctx.triggered:
          raise PreventUpdate
      triggered_id = ctx.triggered[0]["prop_id"]
      if "edit-stash-cancel-btn" not in triggered_id:
          if not any(c for c in edit_clicks if c):
              raise PreventUpdate
  ```

- [x] **Step 2: Remove unused search-category input in handle_search**
  Remove the unused `search-category` State from the `handle_search` callback inputs and signature.
  Code change:
  ```python
  @callback(
      Output("app-results", "children"),
      Input("search-button", "n_clicks"),
      State("search-query", "value"),
      State("search-sort", "value"),
  )
  def handle_search(n_clicks, query, sort):
      if not query:
          raise PreventUpdate
      return CONTROLLER.search_yarn(query=query, sort=sort)
  ```

---

### Task 2: Map search-sort value and remove dead code store

**Files:**
- Modify: `stashies/app_controller.py`

- [x] **Step 1: Map best_match sort option to best**
  Modify `search_yarn` in `stashies/app_controller.py` to map `"best_match"` to Ravelry's expected `"best"` API parameter.
  Code change:
  ```python
      def search_yarn(
          self,
          query: str,
          sort: str = "best",
      ) -> dbc.Col:
          # Map UI sort options to Ravelry API values
          sort_map = {
              "best_match": "best",
              "highest_rating": "rating",
              "most_projects": "projects",
          }
          api_sort = sort_map.get(sort, "best")
          yarns = self.MODEL.search_yarn(query=query, sort=api_sort)
      ```

- [x] **Step 2: Remove memory-output store**
  Remove `dcc.Store(id='memory-output')` from the layout in `stashies/app_controller.py` (line 148).

---

### Task 3: Improve code guards in yarn.py and projects.py

**Files:**
- Modify: `stashies/dataclasses/yarn.py`
- Modify: `stashies/components/projects.py`

- [x] **Step 1: Add name key guard in set_colorway_list**
  Guard against missing `'name'` keys in colorway list dictionary items in `stashies/dataclasses/yarn.py`.
  Code change:
  ```python
      @field_validator('colorways', mode='before')
      def set_colorway_list(
          cls, v: Optional[List[Dict[str, Any]]]
      ) -> Union[List[str], None]:
          if v is not None:
              return sorted(set([colorway['name'] for colorway in v if colorway and 'name' in colorway]))
          return v
  ```

- [x] **Step 2: Simplify photo check in projects.py**
  Simplify list length checks in `stashies/components/projects.py`.
  Code change:
  ```python
          elif p.get("photos"):
              photos = p.get("photos")
              if photos:
                  photo_url = photos[0].get("medium_url") or photos[0].get("square_url") or photos[0].get("thumbnail_url")
  ```

---

### Task 4: Verification

**Files:**
- Modify: `StashStats.md`

- [x] **Step 1: Run tests**
  Command: `.venv/bin/pytest`
  Expected: PASS

- [x] **Step 2: Update checkboxes in StashStats.md**

- [x] **Step 3: Commit changes**
  Command: `git add . && git commit -m "refactor: resolve various warnings and minor issues"`
