---
title: App Configuration and Storage API
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, app, config, kv-storage]
sources: [raw/articles/ravelry-api-reference.md, src/stashstats/client.py]
confidence: high
---

# App Configuration and Storage API

Ravelry provides dedicated cloud key-value storage for third-party applications to sync user preferences, settings, and state across devices.

## Endpoints

- `GET /app/data/get.json?keys=key1+key2`: Retrieve stored user key/value pairs.
- `POST /app/data/set.json`: Store user-specific application data via query/body parameters.
- `POST /app/data/delete.json`: Delete key/value entries.
- `POST /app/config/set.json`: Configure app-level settings (e.g. `profile_badge=1`).

## StashStats Key Usage Conventions

| Key Pattern | Value Schema | Description |
|---|---|---|
| `stash_history_{stash_id}` | JSON array of `StashHistoryEntry` | Chronological quantity modification timeline (`timestamp`, `skeins`, `total_grams`, `total_yards`) |

## Client Methods
- `client.get_app_data(keys: list[str]) -> dict[str, str]`
- `client.set_app_data(**key_values: str) -> dict[str, str]`
- `client.delete_app_data(keys: list[str]) -> dict[str, str]`
- `client.get_stash_history(stash_id: int) -> StashHistory`
- `client.get_batch_stash_history(stash_ids: list[int]) -> dict[int, StashHistory]`
- `client.record_stash_snapshot(stash_item: StashItem) -> StashHistory`
- `client.delete_stash_history(stash_id: int) -> dict[str, str]`

---

## Related
- [[auth-and-permissions]]
- [[api-people-and-current-user]]
- [[stash-model]]
- [[module-client]]
