# Implementation Plan: Log Project Details on Stash Usage Logging

## Phase 1: History Model & apply_usage_to_stash Project Metadata (TDD)
- [x] Task: Unit tests for `StashHistoryEntry` project metadata and `apply_usage_to_stash` [7473187]
- [x] Task: Update `StashHistoryEntry` in `src/stashstats/models/history.py` and `apply_usage_to_stash` in `src/stashstats/web/components/modal.py` [7473187]
- [x] Task: Phase 1 Checkpoint [7473187]

## Phase 2: Log Usage Modal UI & History Table Display (TDD)
- [ ] Task: Unit tests for project/pattern inputs and usage history table display
- [ ] Task: Add project inputs to 'Log Usage' tab and display project column in `create_usage_history_table` in `src/stashstats/web/components/modal.py`
- [ ] Task: Phase 2 Checkpoint

## Phase 3: Modal Callbacks & Full Verification (TDD)
- [ ] Task: Unit tests for `handle_save_modal` callback saving project metadata
- [ ] Task: Wire project inputs into `src/stashstats/web/callbacks/modal.py`
- [ ] Task: Phase 3 Checkpoint & Full Verification
