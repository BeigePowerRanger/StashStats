---
title: Stash Consumption Velocity & Horizon Analytics
created: 2026-08-18
updated: 2026-08-18
type: concept
tags: [stashstats, data-pipeline, stash]
sources: [docs/plans/consumption-velocity-analytics.md, src/stashstats/models/history.py]
confidence: high
---

# Stash Consumption Velocity & Horizon Analytics

Analytics engine specification for calculating historical craft consumption rates, projecting inventory lifespans, and tracking craft burn rates across time.

## Core Analytics Dimensions

### 1. Consumption Velocity Calculation
Measures crafting consumption over discrete trailing time windows (30-day, 90-day, 365-day, and all-time):
- **Grams / Month**: `(Total Grams Consumed in Window) / (Days in Window / 30.44)`
- **Yards / Month**: `(Total Yards Consumed in Window) / (Days in Window / 30.44)`
- **Skeins / Month**: `(Total Skeins Consumed in Window) / (Days in Window / 30.44)`

### 2. Lifespan Horizon Projection
Projects estimated time until current active inventory reaches zero under sustained velocity:
- **Horizon (Months)**: `Current Active Inventory (g / yds) / Average Monthly Velocity`
- **Horizon (Years)**: `Horizon Months / 12`
- **Exclusions**: Stash items with `stash_status` marked as "Will trade/sell", "Used up", or archived.

### 3. Net Accumulation vs. Depletion Rate
Tracks monthly stash inflow versus craft outflow:
- `Net Delta = Stashed Quantity (Inflow) - Logged Usage (Outflow)`
- Visualized as dual-direction bar charts / waterfall charts in the UI.

---

## Data Sources & Dual-Write Pipeline
- **Ravelry Stash API**: Quantities stored on [[stash-model]] records and packs (`POST /people/{username}/stash/{id}.json`).
- **Timeline Ledger**: JSON payload stored in Ravelry [[api-app-and-config]] (`app_data`) holding append-only [[history-model|StashHistoryEntry]] items.

---

## Related
- [[stash-model]]
- [[project-model]]
- [[web-app-specification]]
- [[codebase-architecture]]
- [[api-app-and-config]]
