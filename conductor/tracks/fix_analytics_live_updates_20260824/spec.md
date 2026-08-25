# Specification: Fix Live Data Updates for Projects Made and Monthly Flow Charts

### 1. Overview
Fix data pipeline and reactive callback wiring so that "Projects Made from Stash" and "Monthly Stash Flow" charts in Stash Analytics automatically update with real data from user stash items, logged usage history, pack allocations, and Ravelry projects.

### 2. Functional Requirements
- **Project Usage Correlation Enhancement (`projects.py`)**:
  - Update `StashProjectUsageCalculator.correlate_projects_and_stash` to extract usage records not only from external `Project` objects, but also from:
    1) Stash item `packs` containing project IDs / names.
    2) `histories` ledger entries recorded with `project_name` / `pattern_name`.
    3) Embedded stash item history snapshots.
- **Stash Velocity & Monthly Flow Computation (`velocity.py`)**:
  - Update `StashVelocityCalculator` to automatically synthesize baseline acquisition events from `stash_items`' `created_at` timestamps when explicit histories are empty, and incorporate usage/consumption delta events.
- **Analytics Reactive Callbacks & Stores (`callbacks/analytics.py`, `layouts/stash.py`)**:
  - Update `update_analytics_dashboard` callback to accept histories and project stores (or client fetch), ensuring real-time chart updates whenever stash data or usage is logged.

### 3. Acceptance Criteria
- "Projects Made from Stash" chart renders pie slices when usage history or project packs are present.
- "Monthly Stash Flow" chart renders monthly acquired and consumed bars based on stash creation dates and consumption events.
- Unit tests verify correlation from history entries and automatic acquisition event synthesis.
- 100% automated test pass rate with coverage >80%.
