# Implementation Plan: Subtrack Phase 2 - Stash & History Models

## Task 1: Stash Models & Tests (TDD)
- [x] Subtask 1.1: Write unit tests in `tests/models/test_stash.py` for `StashStatus`, `Pack`, `StashYarn`, `StashItem`, and response envelopes.
- [x] Subtask 1.2: Refine `src/stashstats/models/stash.py` (e.g. use `Field(default_factory=list)` for list fields).
- [x] Subtask 1.3: Run `pytest tests/models/test_stash.py` and ensure passing.

## Task 2: History Models & Timestamp Parsing (TDD)
- [x] Subtask 2.1: Write unit tests in `tests/models/test_history.py` testing `StashHistoryEntry.datetime` against Ravelry timestamp formats (`YYYY/MM/DD HH:MM:SS ±ZZZZ`, ISO format, invalid values) and `StashHistory`.
- [x] Subtask 2.2: Refine `src/stashstats/models/history.py` and verify property parsing.
- [x] Subtask 2.3: Run `pytest tests/models/test_history.py` and ensure passing.

## Task 3: Quality Check & Phase Checkpoint
- [x] Subtask 3.1: Run `ruff check .` and `pytest`.
- [x] Subtask 3.2: Mark Subtrack Phase 2 complete and scaffold Phase 3 (`phase3_app_data_client`).

