# Implementation Plan: Track Projects Made from Stash Yarn

## Phase 1: Data Models & Usage Analytics Engine (TDD)
- [x] Task: Unit tests for `ProjectUsageRecord` and `StashProjectUsageCalculator` [45bfd54]
- [x] Task: Implement `ProjectUsageRecord` model in `src/stashstats/models/analytics.py` [45bfd54]
- [x] Task: Implement `StashProjectUsageCalculator` in `src/stashstats/analytics/projects.py` [45bfd54]
- [x] Task: Phase 1 Checkpoint [45bfd54]

## Phase 2: 'Projects Made from Stash' Pie Chart (TDD)
- [x] Task: Unit tests for `create_projects_pie_chart` across unit dimensions (yards, meters, grams, skeins) [2caa796]
- [x] Task: Implement `create_projects_pie_chart` in `src/stashstats/web/components/analytics_charts.py` [2caa796]
- [x] Task: Phase 2 Checkpoint [2caa796]

## Phase 3: Analytics Layout & Callback Integration (TDD)
- [ ] Task: Unit tests for analytics layout & callbacks containing projects chart
- [ ] Task: Embed 'Projects Made from Stash' chart into `src/stashstats/web/layouts/analytics.py` and reactive callbacks
- [ ] Task: Phase 3 Checkpoint

## Phase 4: Stash Item Modal & Row Project Badges (TDD)
- [ ] Task: Unit tests for linked project consumption display in stash modal/view
- [ ] Task: Render linked project badges/history in `src/stashstats/web/components/modal.py`
- [ ] Task: Phase 4 Checkpoint & Full Verification
