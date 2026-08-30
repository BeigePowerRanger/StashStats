# Implementation Plan: Projects Tab Accordion Layout Refactor

## Phase 1: Project Filtering, Sorting, and Pagination Core Engine (TDD)
- [ ] Task: Write unit tests for project filtering, sorting, and pagination
  - [ ] Write unit tests for `filter_projects` with search queries matching name, pattern, craft, status, and tags in `tests/web/test_projects.py`
  - [ ] Write unit tests for `sort_projects` with `date_desc`, `name_asc`, `progress_desc`, and `status_asc`
  - [ ] Write unit tests for `paginate_projects` validating page bounds and empty states
- [ ] Task: Implement project filtering, sorting, and pagination logic
  - [ ] Implement `filter_projects` in `src/stashstats/web/components/projects.py`
  - [ ] Implement `sort_projects` in `src/stashstats/web/components/projects.py`
  - [ ] Implement `paginate_projects` in `src/stashstats/web/components/projects.py`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Project Accordion UI Components & Layout Construction (TDD)
- [ ] Task: Write unit tests for project accordion UI components and controls
  - [ ] Write tests for `create_project_accordion_item` validating header content (photo, title, badges) and body content (progress bar, metadata, PDF section)
  - [ ] Write tests for `create_grouped_projects_accordion` handling empty list and populated list
  - [ ] Write tests for `create_projects_layout` verifying inclusion of search input, sort dropdown, pagination, spinner, and accordion container
- [ ] Task: Implement accordion components and updated layout
  - [ ] Implement `create_project_accordion_item` and `create_grouped_projects_accordion` in `src/stashstats/web/components/projects.py`
  - [ ] Update `src/stashstats/web/layouts/projects.py` to structure the layout with search bar, sort dropdown, accordion container, and pagination
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Reactive View Callbacks & PDF Integration (TDD)
- [ ] Task: Write unit tests for reactive project view callbacks
  - [ ] Write tests for `update_projects_view_logic` handling search, sort, page change, and store updates
  - [ ] Write tests ensuring PDF upload, delete, and view button callbacks resolve correctly with accordion item structures
- [ ] Task: Implement reactive callbacks and integrate with PDF handlers
  - [ ] Implement `update_projects_view_logic` and callback registration in `src/stashstats/web/callbacks/projects.py`
  - [ ] Verify PDF action callbacks (`handle_pdf_upload`, `handle_pdf_delete`, `handle_pdf_view`) and sync callback work seamlessly
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Full System Verification & Coverage
- [ ] Task: Comprehensive test execution and code quality validation
  - [ ] Run full test suite (`pytest`) and verify code coverage (>80%)
  - [ ] Verify clean linting and type checks
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
