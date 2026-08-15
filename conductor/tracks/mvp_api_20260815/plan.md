# Implementation Plan: MVP API Functionality & History Tracking

## Phase 1: Reference and Yarn Pydantic Models
- **Status**: [x] Completed
- **Subtrack Link**: [subtracks/phase1_yarn_reference/](./subtracks/phase1_yarn_reference/)
- **Scope**: Complete models in `reference.py` and `yarn.py`, full deserialization test coverage in `tests/models/test_reference.py` and `tests/models/test_yarn.py`.

## Phase 2: Stash and History Models
- **Status**: [x] Completed
- **Subtrack Link**: [subtracks/phase2_stash_history/](./subtracks/phase2_stash_history/)
- **Scope**: `StashItem`, `StashHistoryEntry`, timezone parsing, deserialization test suite.

## Phase 3: App Data API Client Integration
- **Status**: [x] Completed
- **Subtrack Link**: [subtracks/phase3_app_data_client/](./subtracks/phase3_app_data_client/)
- **Scope**: `get_app_data`, `set_app_data`, `get_stash_history`, `record_stash_snapshot` auto-deduplication, HTTPX mock tests.
