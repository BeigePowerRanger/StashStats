# Implementation Plan: Subtrack Phase 1 - Reference & Yarn Models

## Task 1: Reference Models & Tests (TDD)
- [x] Subtask 1.1: Write unit tests in `tests/models/test_reference.py` for `ColorFamily`, `YarnWeightReference`, and `FiberCategory`.
- [x] Subtask 1.2: Verify and refine `src/stashstats/models/reference.py` against test suite.
- [x] Subtask 1.3: Run `pytest tests/models/test_reference.py` and ensure passing.

## Task 2: Yarn Models & Response Envelopes (TDD)
- [x] Subtask 2.1: Write unit tests in `tests/models/test_yarn.py` for `FiberType`, `YarnFiber`, `Colorway`, `Yarn`, `YarnSearchResult`, `YarnSearchResponse`, `YarnDetailResponse`.
- [x] Subtask 2.2: Verify and refine `src/stashstats/models/yarn.py` against test suite.
- [x] Subtask 2.3: Run `pytest tests/models/test_yarn.py` and ensure passing.

## Task 3: Quality Check & Phase Checkpoint
- [x] Subtask 3.1: Run `ruff check .` and `pytest`.
- [x] Subtask 3.2: Document Phase 1 results / model exports in subtrack review.
- [x] Subtask 3.3: Mark Subtrack Phase 1 complete and scaffold Phase 2 (`phase2_stash_history`).

