---
title: History Data Model
created: 2026-08-18
updated: 2026-08-18
type: entity
tags: [model, stashstats, stash, data-pipeline]
sources: [src/stashstats/models/history.py, docs/plans/stash-history-app-data.md]
confidence: high
---

# History Data Model

Tracks temporal inventory adjustments, usage deductions, and historical stash balance snapshots stored in Ravelry's `app_data` cloud key-value store.

## Core Schema Fields (`stashstats.models.history`)

### 1. `StashHistoryEntry`
Snapshot representing an individual usage event or point-in-time quantity state:
- `id` (`str | None`): Unique change event identifier.
- `date` (`str | None`): Date of change (ISO `YYYY-MM-DD`).
- `timestamp` (`str`): Ravelry formatted timestamp string.
- `skeins` (`float`): Remaining skeins or applied skein deduction.
- `yards` (`float | None`): Deducted or applied yardage.
- `grams` (`float | None`): Deducted or applied weight in grams.
- `total_grams` (`float`): Cumulative item balance in grams.
- `total_yards` (`float`): Cumulative item balance in yards.
- `pack_id` (`int | None`): Associated target pack record ID.
- `delta_skeins` (`float | None`): Explicit signed quantity delta (negative for usage deductions).
- `notes` (`str | None`): Project, recipient, or usage event note.

### 2. `StashHistory`
Timeline container aggregating all historical events for a single stash item:
- `stash_id` (`int`): Linked [[stash-model]] identifier.
- `entries` (`list[StashHistoryEntry]`): Chronological sequence of usage events and adjustments.

---

## Dual-Write Persistence Architecture
1. **Ravelry Stash API**: Updates live pack and skein balances on the core entity (`POST /people/{username}/stash/{id}.json`).
2. **App Data Timeline**: Persists the append-only history ledger to `POST /people/{username}/app_data/{key}.json` as JSON string payloads.

---

## Related
- [[stash-model]]
- [[api-app-and-config]]
- [[consumption-velocity-analytics]]
- [[codebase-architecture]]
- [[module-client]]
