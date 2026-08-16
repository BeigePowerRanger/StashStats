# Implementation Plan: Yarn Search Integration

## Phase 1: Pydantic Models & API Client Expansion
- [x] Task: Strengthen Data Models (TDD)
    - [x] Sub-task: Write tests in `tests/models/test_yarn.py` for handling missing data, edge cases, and inconsistent API results.
    - [x] Sub-task: Update `Yarn` and related Pydantic models in `src/stashstats/models/` with `@field_validator` and `@model_validator` to enforce data consistency.
    - [x] Sub-task: Replace open-ended `| None` fields with strict validation logic where applicable.
- [x] Task: Update `RavelryClient` for Yarn Search (TDD)
    - [x] Sub-task: Write tests in `tests/test_client.py` for the yarn search endpoint.
    - [x] Sub-task: Implement `search_yarns` method in `src/stashstats/client.py`.
    - [x] Sub-task: Run `pytest` and verify the client correctly parses the API response.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Pydantic Models & API Client Expansion' (Protocol in workflow.md)

## Phase 2: Search UI Components & Layout
- [x] Task: Build Search Form & Accordion Components (TDD)
    - [x] Sub-task: Write tests in `tests/web/test_yarn_search.py` for search inputs, pagination, and accordion rendering.
    - [x] Sub-task: Implement search layout and accordion components in `src/stashstats/web/layouts/search.py` and `src/stashstats/web/components/search.py`.
    - [x] Sub-task: Integrate the layout into the "Yarn Search" tab in `src/stashstats/web/layouts/main.py`.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Search UI Components & Layout' (Protocol in workflow.md)

## Phase 3: Reactive Callbacks & Integration
- [x] Task: Connect UI to API via Callbacks (TDD)
    - [x] Sub-task: Write tests for callback logic handling API requests and pagination state.
    - [x] Sub-task: Implement reactive callbacks in `src/stashstats/web/callbacks/search.py` to trigger API searches and update the accordion and pagination elements.
    - [x] Sub-task: Run full test suite (`pytest`) and `ruff check .` to verify integration.

- [ ] Task: Conductor - User Manual Verification 'Phase 3: Reactive Callbacks & Integration' (Protocol in workflow.md)
