# Subtrack Specification: Phase 3 - App Data API Client Integration

## Overview
Implement, refine, and test the Ravelry App Data API client methods and automated quantity history tracking, snapshot recording, and deduplication logic using Phase 1 and Phase 2 models.

## Functional Requirements
1. **App Data Methods (`src/stashstats/client.py`)**:
   - `get_app_data(keys: list[str]) -> dict[str, str]`: Calls `GET /app/data/get.json` with space-delimited keys and parses response.
   - `set_app_data(**key_values: str) -> dict[str, str]`: Calls `POST /app/data/set.json` with key-value params.
   - `delete_app_data(keys: list[str]) -> dict[str, str]`: Calls `POST /app/data/delete.json` with space-delimited keys.

2. **History Management & Auto-Deduplication**:
   - `get_stash_history(stash_id: int) -> StashHistory`: Retrieves and deserializes `stash_history_{id}`.
   - `get_batch_stash_history(stash_ids: list[int]) -> dict[int, StashHistory]`: Batch retrieves histories in one request.
   - `record_stash_snapshot(stash_item: StashItem, timestamp: str | None = None) -> StashHistory`:
     - Compares snapshot quantity metrics (`skeins`, `total_grams`, `total_yards`) against the most recent entry.
     - If quantity hasn't changed, skips appending to prevent timeline noise.
     - If quantity has changed, appends new snapshot and persists to App Data.
   - `delete_stash_history(stash_id: int) -> dict[str, str]`: Removes app data key on stash deletion.

3. **Mocking & Integration Test Suite (`tests/test_client.py`)**:
   - HTTP mock tests using `httpx.Response` / pytest fixtures for `get_app_data`, `set_app_data`, `delete_app_data`.
   - History deduplication unit tests verifying duplicate entries are not appended.
   - History change tests verifying new entries are appended and saved.
   - Batch retrieval tests verifying multiple records are processed correctly.

## Acceptance Criteria
- [ ] App Data methods correctly format query parameters and decode responses.
- [ ] Auto-deduplication prevents recording redundant history entries when quantities do not change.
- [ ] 100% test pass rate with `pytest tests/`.
- [ ] Lint check passes with `ruff check`.
