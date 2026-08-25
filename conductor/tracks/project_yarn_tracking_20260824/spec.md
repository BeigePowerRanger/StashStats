# Specification: Track Projects Made from Stash Yarn & Analytics Breakdown

## 1. Overview
Track and visualize what projects were created with stash yarn. When yarn is consumed or allocated to projects, identify the associated Ravelry project (and pattern), displaying both an aggregate 'Projects Made from Stash' pie chart in Stash Analytics and linked project badges/history on individual stash item detail modals.

## 2. Functional Requirements
- **Project-Yarn Usage Modeling**:
  - `ProjectUsageRecord`: models project consumption linkage (`project_id`, `project_name`, `pattern_name`, `status_name`, `completed_date`, `stash_id`, `yarn_name`, `yards_used`, `meters_used`, `grams_used`, `skeins_used`).
  - `StashProjectUsageCalculator`: correlates stash items, packs, and project allocations to compute project-level consumption metrics.
- **Stash Analytics Visualizations**:
  - **'Projects Made from Stash' Chart (`create_projects_pie_chart`)**: Donut/pie chart displaying the proportion of stashed yarn consumed across user projects, dynamically scaled by the selected unit (Yards, Meters, Grams, Skeins).
- **Stash Item View & Detail Modal**:
  - Display linked project history/badges on stash item details/modal showing which projects used that specific yarn.
- **Reactive UI & Testing**:
  - Full unit tests for aggregation, chart rendering, and Dash layout/callbacks.

## 3. Acceptance Criteria
- Unit tests cover model parsing, calculation logic, and chart rendering.
- Stash Analytics tab includes "Projects Made from Stash" visualization with dynamic unit switching.
- Stash detail modal lists linked projects that consumed portions of that stash yarn.
- 100% automated test pass rate with coverage >80%.
