---
title: Stash API Endpoints
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, stash, yarn]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Stash API Endpoints

The Stash API provides methods for searching, querying, creating, modifying, and organizing yarn and fiber stashes.

## Endpoints Summary

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/people/{username}/stash/list.json` | List and search user's stash items | Yes |
| `GET` | `/people/{username}/stash/{id}.json` | Get single stash record details | Yes |
| `POST` | `/people/{username}/stash/create.json` | Create a new stash item | Yes |
| `POST` | `/people/{username}/stash/{id}.json` | Update an existing stash item | Yes |
| `DELETE` | `/people/{username}/stash/{id}.json` | Delete a stash item | Yes |
| `GET` | `/people/{username}/stash/comments.json`| List comments on stash items | Yes |

## Query Parameters for `/people/{username}/stash/list.json`

- `query`: Text search term across stash entries.
- `yarn_id`: Filter stash entries matching a specific [[yarn-model]].
- `fiber_id`: Filter by fiber record.
- `stash_status_id`: Filter by stash status (e.g. in stash, used up, traded).
- `sort`: Sorting field (e.g. `created_`, `yarn_name`, `rating`).
- `page`: Page index (default: `1`).
- `page_size`: Items per page (default: `25`, max: `100`).

## Return Models
- Returns arrays of [[stash-model]] (`Stash (list)` or `Stash (full)`), [[pack-model]] (`Pack`), and [[paginator-model]] (`Paginator`).

---

## Related
- [[stash-model]]
- [[yarn-model]]
- [[pack-model]]
- [[colorway-model]]
- [[input-objects-and-post-data]]
- [[pagination-and-sorting]]
- [[auth-and-permissions]]
