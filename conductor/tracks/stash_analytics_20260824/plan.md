# Track Plan: Stash Consumption Velocity & Analytics Engine

## Phase 1: Analytics Data Models & Calculation Engine [checkpoint: 7f63b51]
- [x] Task: Create analytics models (`StashDeltaEvent`, `PeriodicRollup`, `RollingVelocity`, `StashHorizon`, `StashVelocityReport`) in `src/stashstats/models/analytics.py` [5dbc6f7]
    - [x] Create tests in `tests/test_analytics_models.py`
    - [x] Implement models in `src/stashstats/models/analytics.py` and export in `src/stashstats/models/__init__.py`
- [x] Task: Implement `StashVelocityCalculator` in `src/stashstats/analytics/velocity.py` [fd800aa]
    - [x] Create tests in `tests/test_analytics_velocity.py`
    - [x] Implement event extraction, periodic rollups, rolling velocity windows, and lifespan horizon calculations
- [x] Task: Implement stash inventory distribution aggregators [ba69afd]
    - [x] Create tests in `tests/test_analytics_distributions.py`
    - [x] Implement distribution functions for yarn weight, fiber content, color family, and brand aggregations
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Client & Storage Integration [checkpoint: 2f3c461]
- [x] Task: Implement `get_stash_velocity_report` on `RavelryClient` [4747a35]
    - [x] Create tests in `tests/test_client_analytics.py`
    - [x] Implement client method to fetch stash, batch load quantity history, and generate velocity report
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Dash Components, Charts & Analytics Layout
- [x] Task: Implement Plotly chart generators in `src/stashstats/web/components/analytics_charts.py` [601febf]
    - [x] Create tests in `tests/test_web_analytics_charts.py`
    - [x] Implement fiber donut chart, weight distribution bar chart, monthly flow chart, and velocity trend charts
- [x] Task: Implement KPI summary metric cards and filter controls in `src/stashstats/web/components/analytics.py` [4cebbb9]
    - [x] Create tests in `tests/test_web_analytics_components.py`
    - [x] Implement summary cards (active yards/skeins/items, pace, lifespan) and interactive filter bar components
- [ ] Task: Implement Stash Analytics layout and wire into navigation tabs
    - [ ] Create tests in `tests/test_web_analytics_layout.py`
    - [ ] Build `src/stashstats/web/layouts/analytics.py` and embed in `src/stashstats/web/layouts/main.py`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Dash Callbacks & End-to-End Verification
- [ ] Task: Implement reactive callbacks for Stash Analytics in `src/stashstats/web/callbacks/analytics.py`
    - [ ] Create tests in `tests/test_web_callbacks_analytics.py`
    - [ ] Implement filter callbacks and metric/chart update handlers
- [ ] Task: Register callbacks in `src/stashstats/web/app.py` and verify full suite
    - [ ] Register analytics callbacks in Dash app factory
    - [ ] Run full automated test suite and Playwright/UI integration checks
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
