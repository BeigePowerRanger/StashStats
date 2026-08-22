---
title: Global Search API
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, search]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Global Search API

Global text search across all entity types in Ravelry.

## Endpoint

`GET /search.json`

### Parameters
- `query`: Text string to search.
- `limit`: Number of results (default `50`, max `500`).
- `types`: Space-delimited list of entity types to include: `User`, `PatternAuthor`, `PatternSource`, `Pattern`, `YarnCompany`, `Yarn`, `Group`, `Event`, `Project`, `Page`, `Topic`, `Shop`.

### Result Object Structure
Each match returns title, `type_name`, thumbnail URLs, and a nested `record` object (`type`, `id`, `permalink`, `uri`).

---

## Related
- [[api-yarns-and-companies]]
- [[api-patterns-and-sources]]
- [[api-stash]]
