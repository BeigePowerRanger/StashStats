---
title: Module - Client
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [stashstats, client, endpoint, pagination, stash]
sources: [src/stashstats/base.py, src/stashstats/client.py]
confidence: high
---

# Client & HTTP Request Architecture

StashStats implements a streamlined synchronous HTTP client architecture built on `httpx`:

```text
src/stashstats/
├── base.py           # BaseAPIClient (HTTP session mechanics & connection pooling)
└── client.py         # RavelryClient (Domain API methods)
```

## 1. Base Engine (`stashstats.base.BaseAPIClient`)
- **Pydantic `BaseModel`**: Strict `model_config` (`validate_assignment=True`, `extra="forbid"`, `str_strip_whitespace=True`).
- **Connection Lifecycle**: Supports one-off calls (`client.get(...)`) and pooled multi-request sessions with context managers (`with RavelryClient() as client:`).
- **Parameter Formatting**: Automatic removal of `None` keys from query dictionaries.
- **Error Dispatching**: Translates HTTP 4xx/5xx responses into typed exceptions via [[module-exceptions]].

## 2. Domain Client (`stashstats.client.RavelryClient`)
Exposes high-level typed domain endpoints:
- `get_current_user()`: Identity verification against `/current_user.json` ([[api-people-and-current-user]]).
- `search_yarns(query, page, page_size, sort, personal_attributes)`: Fulltext yarn searches returning `YarnSearchResponse` ([[api-yarns-and-companies]]).
- `get_stash_list(username, page, page_size, sort, ...)`: Paginated stash list for specified username returning `StashListResponse` ([[api-stash]]).
- `get_my_stash(username, page, page_size, sort, ...)`: Helper fetching current authenticated user's stash.
- `get_stash_item(stash_id, username)`: Fetch full details for a single stash entry returning `StashItem`.
- `create_stash_item(yarn_id, colorway_name, dye_lot, skeins, total_grams, total_yards, location, ...)`: Add a catalog yarn into the user's stash (`POST /people/{username}/stash/create.json`).
- `update_stash_item(stash_id, location, colorway_name, dye_lot, stash_status_id, skeins, total_grams, total_yards, ...)`: Modify existing stash record (`POST /people/{username}/stash/{id}.json`).
- `delete_stash_item(stash_id, username)`: Delete a stash entry (`DELETE /people/{username}/stash/{id}.json`).
- `get_app_data(keys: list[str]) -> dict[str, str]`: Retrieve stored user key/value pairs (`GET /app/data/get.json`).
- `set_app_data(**key_values: str) -> dict[str, str]`: Store user-specific application data (`POST /app/data/set.json`).
- `delete_app_data(keys: list[str]) -> dict[str, str]`: Delete key/value entries (`POST /app/data/delete.json`).
- `get_stash_history(stash_id: int) -> StashHistory`: Retrieve quantity change timeline (`timestamp`, `skeins`, `total_grams`, `total_yards`).
- `get_batch_stash_history(stash_ids: list[int]) -> dict[int, StashHistory]`: Batch load history for multiple items in one request.
- `record_stash_snapshot(stash_item: StashItem, timestamp: str | None) -> StashHistory`: Record snapshot in App Data.
- `delete_stash_history(stash_id: int) -> dict[str, str]`: Remove App Data history key.
- `get_yarn_details(yarn_id: int) -> YarnDetailResponse`: Fetch full yarn profile including fiber composition and colorways (`GET /yarns/{id}.json`).
- `search_stash(query: str, page, page_size, sort) -> StashSearchResponse`: Search public stashes across Ravelry (`GET /stash/search.json`).
- `get_color_families() -> list[ColorFamily]`: Reference list of color families (`GET /color_families.json`).
- `get_yarn_weights() -> list[YarnWeightReference]`: Reference list of yarn weight classifications (`GET /yarn_weights.json`).
- `get_fiber_categories() -> list[FiberCategory]`: Reference list of fiber categories (`GET /fiber_categories.json`).

## Usage Example
```python
from stashstats import RavelryClient

with RavelryClient() as client:
    # Fetch authenticated user's stash
    stash_resp = client.get_my_stash()
    for item in stash_resp.stash:
        print(f"{item.name} - {item.primary_pack.quantity_description}")
```

## Cross-References
- [[codebase-architecture]]: Package architecture overview.
- [[module-config]]: Configuration and credentials provider.
- [[module-exceptions]]: Error raising and status code handling.
- [[stash-model]]: Stash item data schemas.
- [[pagination-and-sorting]]: Pagination mechanics.
