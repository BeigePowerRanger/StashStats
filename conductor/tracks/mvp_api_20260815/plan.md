# Implementation Plan: MVP API Functionality & History Tracking

## Phase 1: Reference and Yarn Pydantic Models
- **Status**: [ ] In Progress / Ready
- **Subtrack Link**: [subtracks/phase1_yarn_reference/](./subtracks/phase1_yarn_reference/)
- **Scope**: Complete models in `reference.py` and `yarn.py`, full deserialization test coverage in `tests/models/test_reference.py` and `tests/models/test_yarn.py`.

## Phase 2: Stash and History Models
- **Status**: [ ] Pending Phase 1 Completion
- **Scope**: `StashItem`, `StashHistoryEntry`, timezone parsing, deduplication helpers. Detailed subtrack generated after Phase 1.

## Phase 3: App Data API Client Integration
- **Status**: [ ] Pending Phase 2 Completion
- **Scope**: `get_app_data`, `set_app_data`, `get_stash_history`, `record_stash_snapshot`, HTTPX mock testing. Detailed subtrack generated after Phase 2.
