# Implementation Plan: Fix 'Add to Stash' Reflection

## Phase 1: Pure Logic & Unit Tests for handle_add_to_stash_logic (TDD)
- [x] Task: Unit tests for `handle_add_to_stash_logic` with client API and offline fallback [1289f70]
- [x] Task: Implement `handle_add_to_stash_logic` in `src/stashstats/web/callbacks/search.py` [1289f70]
- [x] Task: Phase 1 Checkpoint [1289f70]

## Phase 2: Callback Registration & Integration Wiring (TDD)
- [x] Task: Unit tests for `handle_add_to_stash` callback wiring with `stash-raw-store` [1289f70]
- [x] Task: Update `register_search_callbacks` in `src/stashstats/web/callbacks/search.py` [1289f70]
- [x] Task: Phase 2 Checkpoint [1289f70]

## Phase 3: Full Verification & Container Rebuild
- [x] Task: Run complete automated test suite (`pytest tests/`) [1289f70]
- [x] Task: Rebuild Docker container (`docker compose build web_dev`) [1289f70]
- [x] Task: Phase 3 Checkpoint & Track Completion [1289f70]

