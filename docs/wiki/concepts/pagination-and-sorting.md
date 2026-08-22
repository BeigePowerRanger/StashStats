---
title: Pagination and Sorting
created: 2026-08-14
updated: 2026-08-14
type: concept
tags: [pagination, endpoint, protocol]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Pagination and Sorting

The Ravelry API provides a standardized mechanism for pagination and multi-field sorting across list endpoints.

## Pagination Parameters

Methods that support pagination accept the following query parameters:
- `page`: Result page number to retrieve (1-indexed, default: `1`).
- `page_size`: Number of records per page (default: typically `25` or `50`, max: `100` to `500` depending on endpoint).

### The Paginator Object
Paginated responses include a `paginator` metadata object alongside the result list:
- `page`: Current page number.
- `page_count`: Total number of pages available.
- `page_size`: Number of results requested per page.
- `results`: Total count of matching records across all pages.
- `last_page`: Boolean indicating if this is the final page.

See [[paginator-model]] for schema details.

---

## Sorting Rules

Unless otherwise specified, API calls accepting a `sort` parameter have two conventions:
1. **Multiple Sort Orders**: Space-delimited string of sort keys (e.g. `sort=yarn_name rating`).
2. **Descending / Reversed Sort**: Append an underscore `_` suffix to reverse the sort order (e.g. `sort=created_` for newest first, `name_` for Z-A).

---

## Related
- [[paginator-model]]
- [[api-stash]]
- [[api-patterns-and-sources]]
- [[api-projects-and-queue]]
- [[http-status-codes-and-errors]]
