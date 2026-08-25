# Specification: Log Project Details on Stash Usage Logging

## 1. Overview
When a user logs stash yarn usage in the stash item modal, capture the project name and pattern name associated with the yarn consumption. Store this project metadata in the usage history record and display it in the usage history table.

## 2. Functional Requirements
- **Stash Usage Form UI (`modal.py`)**:
  - Add input fields for **Project Name** (`modal-input-project-name`) and **Pattern Name** (`modal-input-pattern-name`) to the "Log Usage" tab of the Stash modal.
- **Data Model & Ledger (`history.py`, `modal.py`)**:
  - Update `StashHistoryEntry` model to support `project_name: str | None = None`, `project_id: int | None = None`, and `pattern_name: str | None = None`.
  - Update `apply_usage_to_stash` to accept `project_name` and `pattern_name`, writing them to the generated usage history entry.
- **Usage History Display**:
  - Update `create_usage_history_table` to include a "Project / Pattern" column displaying the linked project information alongside date, skeins, yards, and weight.
- **Modal Callback Integration (`callbacks/modal.py`)**:
  - Update `handle_save_modal` callback to read `project_name` and `pattern_name` inputs from the DOM and persist them into the usage history.

## 3. Acceptance Criteria
- Stash modal "Log Usage" tab contains project name and pattern name inputs.
- Saving usage preserves project and pattern metadata in history storage.
- Usage history table displays the logged project/pattern name.
- 100% automated test pass rate with coverage >80%.
