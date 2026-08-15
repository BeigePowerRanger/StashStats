# Subtrack Specification: Phase 2 - Stash and History Models

## Overview
Implement, refine, and test Pydantic models for Ravelry Stash structures (`StashItem`, `Pack`, `StashStatus`, `StashYarn`, `StashListResponse`, `StashSearchResponse`, `StashDetailResponse`) and App Data History tracking (`StashHistoryEntry`, `StashHistory`) utilizing Phase 1 reference and yarn models.

## Functional Requirements
1. **Stash Models (`src/stashstats/models/stash.py`)**:
   - `StashStatus`: ID and status name.
   - `Pack`: Detailed quantity allocation (skeins, total_grams, total_yards, per-skein metrics, dye lot, purchase info).
   - `StashYarn`: Lightweight embedded yarn representation with `Photo`, `YarnCompany`, `YarnWeight`.
   - `StashItem`: Complete Ravelry `Stash (list)` representation with `packs`, `primary_pack`, `first_photo`, `user`, tags, and timestamp fields.
   - Response envelopes: `StashListResponse`, `StashDetailResponse`, `StashSearchResponse`.

2. **History Models (`src/stashstats/models/history.py`)**:
   - `StashHistoryEntry`: Snapshot of `timestamp`, `skeins`, `total_grams`, `total_yards`.
   - `StashHistoryEntry.datetime`: Robust property parser handling Ravelry timestamp formats (`YYYY/MM/DD HH:MM:SS ±ZZZZ`) and ISO-8601 strings.
   - `StashHistory`: Container for `stash_id` and chronological `entries`.

3. **Validation & Test Suite**:
   - `tests/models/test_stash.py`: Deserialization of stash list records, single stash item details, nested packs, and search envelopes.
   - `tests/models/test_history.py`: Verification of timestamp parsing across standard and edge-case date formats, timezone offsets, and invalid dates.

## Acceptance Criteria
- [ ] All stash and history models pass strict type validation.
- [ ] `StashHistoryEntry.datetime` correctly parses standard Ravelry timestamp formats with offset awareness.
- [ ] 100% test pass rate with `pytest tests/models/test_stash.py tests/models/test_history.py`.
- [ ] Lint check passes with `ruff check`.
