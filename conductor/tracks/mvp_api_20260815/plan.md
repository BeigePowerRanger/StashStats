# Implementation Plan: MVP API Functionality & History Tracking

## Phase 1: Reference and Yarn Pydantic Models
- [ ] Task: Implement Reference Models
    - [ ] Create `ColorFamily`, `YarnWeightReference`, and `FiberCategory` models in `src/stashstats/models/reference.py`
- [ ] Task: Implement Yarn Models
    - [ ] Create `FiberType`, `YarnFiber`, `Colorway`, and `Yarn` models in `src/stashstats/models/yarn.py`
    - [ ] Create `YarnDetailResponse` envelope
- [ ] Task: Test Reference and Yarn Models
    - [ ] Write unit tests for data validation and deserialization in `tests/models/test_yarn.py` and `test_reference.py`

## Phase 2: Stash and History Models
- [ ] Task: Implement Stash Models
    - [ ] Create `StashItem`, `StashSearchResponse`, and `StashDetailResponse` in `src/stashstats/models/stash.py`
- [ ] Task: Implement History Models
    - [ ] Create `StashHistoryEntry` and `StashHistory` in `src/stashstats/models/history.py`
    - [ ] Implement `datetime` property parsing logic on `StashHistoryEntry`
- [ ] Task: Test Stash and History Models
    - [ ] Write unit tests for timezone parsing and data validation in `tests/models/test_history.py` and `test_stash.py`

## Phase 3: App Data API Client Integration
- [ ] Task: Implement Base App Data Methods
    - [ ] Add `get_app_data`, `set_app_data`, and `delete_app_data` to `src/stashstats/client.py`
- [ ] Task: Implement History-Specific Client Methods
    - [ ] Implement `get_stash_history` and `get_batch_stash_history`
    - [ ] Implement `delete_stash_history`
- [ ] Task: Implement History Auto-Deduplication Logic
    - [ ] Implement `record_stash_snapshot(stash_item, timestamp)`
    - [ ] Add logic to fetch latest history, compare timestamp/skeins/grams/yards, and only append if a change occurred
- [ ] Task: Test App Data API Client Methods
    - [ ] Write tests mocking HTTPX for `get_app_data` and `set_app_data`
    - [ ] Write specific tests for the auto-deduplication logic inside `record_stash_snapshot`
