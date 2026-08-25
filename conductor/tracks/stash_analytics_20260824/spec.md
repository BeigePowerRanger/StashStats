# Track Specification: Stash Consumption Velocity & Analytics Engine

## Overview
Implement the comprehensive Stash Analytics dashboard and calculation engine in StashStats. This feature computes consumption velocity, periodic net stash flow (acquired vs consumed yardage/skeins), rolling burn rates (30d/90d/365d), and projected stash lifespan horizons from stash items and App Data quantity history snapshots. It presents these insights through an interactive Dash dashboard featuring KPI cards, dynamic Plotly distribution charts, net flow graphs, and filter controls.

## Functional Requirements
1. **Analytics Data Models (`src/stashstats/models/analytics.py`)**:
   - `StashDeltaEvent`: Represents atomic transition between two stash history snapshots with delta skeins, grams, yards, and timestamp.
   - `PeriodicRollup`: Groups flow events into calendar periods (monthly `YYYY-MM` and yearly `YYYY`) with acquired, consumed, and net yards/skeins.
   - `RollingVelocity`: Trailing burn rates across 30, 90, and 365-day windows (yards/day, yards/month, skeins/month).
   - `StashHorizon`: Calculates remaining active inventory months/years until depletion based on trailing burn rate.
   - `StashVelocityReport`: Composite report combining active totals, periodic rollups, rolling velocities, and horizon projection.

2. **Analytics Engine (`src/stashstats/analytics/velocity.py`)**:
   - `StashVelocityCalculator.extract_events`: Extracts chronological transition events from stash history dictionaries.
   - `StashVelocityCalculator.calculate_periodic_rollups`: Aggregates delta events by month and year.
   - `StashVelocityCalculator.calculate_rolling_velocity`: Computes daily and monthly pace for trailing window horizons.
   - `StashVelocityCalculator.calculate_horizon`: Projects stash exhaustion timeframe.
   - `StashVelocityCalculator.generate_report`: Produces composite `StashVelocityReport`.
   - Distribution aggregators for stash fiber compositions, yarn weights, color families, and brands.

3. **Client & Integration Layer (`src/stashstats/client.py`)**:
   - `RavelryClient.get_stash_velocity_report`: Helper method retrieving user stash, batch loading quantity histories, and calculating the report.

4. **Dash Components & Charts (`src/stashstats/web/components/analytics.py`, `src/stashstats/web/components/analytics_charts.py`)**:
   - KPI Summary Cards: Active yards/skeins/items, trailing 30d/90d burn rate, stash lifespan horizon.
   - Plotly Charts:
     - Fiber composition donut chart.
     - Yarn weight distribution bar chart.
     - Monthly net flow bar chart (Acquired vs Consumed yardage over time).
     - Rolling consumption pace trend graph.
   - Filter bar: Interactive controls for filtering by weight, fiber, status, and time range.

5. **Dash Layout & Reactive Callbacks (`src/stashstats/web/layouts/analytics.py`, `src/stashstats/web/callbacks/analytics.py`)**:
   - Stash Analytics layout integrated into `main-tabs` in `src/stashstats/web/layouts/main.py`.
   - Callbacks for reactive filtering and metric updates.

## Acceptance Criteria
- Unit and component tests achieving >80% test coverage across models, analytics calculations, layout, and callbacks.
- Navigating to the "Stash Analytics" tab displays active metrics, charts, and interactive filter controls.
- Filter selections dynamically update charts and summary metrics.
- Dark theme styling adheres to the StashStats design system (`#222`, `#333`, `#00bc8c`, `bg-dark text-light`).

## Out of Scope
- Direct write mutations to Ravelry from the analytics dashboard.
- Machine learning or predictive deep learning models.
