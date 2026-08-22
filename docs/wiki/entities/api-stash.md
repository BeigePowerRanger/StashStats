---
title: Stash API Endpoints
created: 2026-08-14
updated: 2026-08-18
type: entity
tags: [endpoint, stash, yarn, api-reference]
sources: [raw/articles/ravelry-api-reference.md, live-audit]
confidence: verified
---

# Stash API Endpoints

The Stash API provides methods for searching, querying, creating, modifying, and organizing yarn and fiber stashes.

## Endpoints Summary

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/people/{username}/stash/list.json` | List and filter user's stash items | Yes |
| `GET` | `/people/{username}/stash/{id}.json` | Get single stash record details | Yes |
| `GET` | `/stash/search.json` | Search public stashes across Ravelry | Yes |
| `POST` | `/people/{username}/stash/create.json` | Create a new stash item | Yes |
| `POST` | `/people/{username}/stash/{id}.json` | Update an existing stash item & packs | Yes |
| `DELETE` | `/people/{username}/stash/{id}.json` | Delete a stash item | Yes |
| `GET` | `/people/{username}/stash/comments.json`| List comments on stash items | Yes |

## Endpoint Behaviors & Payload Nuances

### 1. List Endpoint (`GET /people/{username}/stash/list.json`)
- **Root Envelope**: `{"stash": [...], "paginator": {...}}`
- **List Item Properties**: Each entry in `stash` contains core summary fields: `id`, `name`, `permalink`, `colorway_name`, `color_family_name`, `dye_lot`, `location`, `comments_count`, `favorites_count`, `handspun`, `has_photo`, `created_at`, `updated_at`, `tag_names`, `stash_status`, `yarn`, and `primary_pack`.
- **Omitted from List**: The list endpoint intentionally **omits** `packs` (array), `notes`, `notes_html`, `photos` (array), `yarn_weight_name`, and `user`.
- **Quantity Metrics**: Inventory counts (`skeins`, `total_yards`, `total_grams`) must be read from `primary_pack` when consuming the list endpoint.

### 2. Detail Endpoint (`GET /people/{username}/stash/{id}.json`)
- **Root Envelope**: `{"stash": {...}}`
- **Detail Item Properties**: Extends the list item with full collections: `packs: list[Pack]`, `notes: str`, `notes_html: str`, `photos: list[Photo]`, `user: UserProfile`, `yarn_weight_name: str`, `long_yarn_weight_name: str`.

### 3. Update Item & Packs (`POST /people/{username}/stash/{id}.json`)
- To update pack allocations (such as deducting or replenishing skeins), the payload must pass the target pack ID inside the nested `pack` dictionary:
```json
{
  "location": "Bin 3",
  "notes": "Updated notes",
  "stash_status_id": 1,
  "pack": {
    "id": 128288737,
    "skeins": 5.0,
    "total_yards": 1100.0,
    "total_grams": 250.0,
    "colorway": "Aqua",
    "dye_lot": "104"
  }
}
```

### 4. Query Parameters for `/people/{username}/stash/list.json`
- `query`: Text search term across stash entries.
- `yarn_id`: Filter stash entries matching a specific [[yarn-model]].
- `fiber_id`: Filter by fiber record.
- `stash_status_id`: Filter by status (`1`=In stash, `2`=Used up, `3`=Will trade/sell, `4`=Gone/sold).
- `sort`: Sorting field (`created_`, `yarn_name`, `rating`, `colorway`, `dye_lot`).
- `page`: Page index (default: `1`).
- `page_size`: Items per page (default: `25`, max: `100`).

---

## Related
- [[stash-model]]
- [[yarn-model]]
- [[pack-model]]
- [[colorway-model]]
- [[api-app-and-config]]
- [[input-objects-and-post-data]]
- [[pagination-and-sorting]]
- [[auth-and-permissions]]

