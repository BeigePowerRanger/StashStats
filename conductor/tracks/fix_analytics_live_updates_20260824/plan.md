# Implementation Plan: Fix Live Updates for Projects Made and Monthly Flow

## Phase 1: Enhanced Project Usage Extraction & Velocity Baseline Events (TDD)
- [x] Task: Unit tests for `StashProjectUsageCalculator` extracting usage from `histories` entries and stash item `packs` [44b62bc]
- [x] Task: Unit tests for `StashVelocityCalculator` synthesizing baseline acquisition events from `stash_items`' `created_at` [44b62bc]
- [x] Task: Implement project usage extraction in `src/stashstats/analytics/projects.py` [44b62bc]
- [x] Task: Implement baseline event synthesis in `src/stashstats/analytics/velocity.py` [44b62bc]
- [x] Task: Phase 1 Checkpoint [44b62bc]

## Phase 2: Analytics Callback Wiring & Live Data Stores (TDD)
- [x] Task: Unit tests for `update_analytics_dashboard_logic` with history and project data [90d1967]
- [x] Task: Update `update_analytics_dashboard` callback in `src/stashstats/web/callbacks/analytics.py` and layout stores [90d1967]
- [x] Task: Phase 2 Checkpoint [90d1967]

## Phase 3: Full Verification & Container Rebuild
- [ ] Task: Run complete automated test suite (`pytest tests/`)
- [ ] Task: Rebuild Docker container (`docker compose build web_dev`)
- [ ] Task: Phase 3 Checkpoint & Track Completion
