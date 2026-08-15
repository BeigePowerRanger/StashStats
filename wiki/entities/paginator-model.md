---
title: Paginator Model
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [model, pagination, protocol]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Paginator Model

Standard response envelope accompanying all paginated API queries.

## Schema Fields

| Field Name | Type | Description |
|---|---|---|
| `page` | Integer | Current active page (1-indexed) |
| `page_count` | Integer | Total number of pages |
| `page_size` | Integer | Number of items per page |
| `results` | Integer | Total count of matching items across all pages |
| `last_page` | Boolean | True if current page is the final page |

---

## Related
- [[pagination-and-sorting]]
- [[api-stash]]
- [[api-patterns-and-sources]]
