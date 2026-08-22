---
title: Patterns and Pattern Sources API
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, pattern, model, search]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Patterns and Pattern Sources API

Endpoints for searching pattern databases, fetching pattern attributes, yarn requirements, needle recommendations, and source publications.

## Endpoints

### Patterns
- `GET /patterns/search.json`: Advanced pattern search with filters (craft, needle size, yardage, category, difficulty).
- `GET /patterns/{id}.json`: Complete pattern metadata, yarn requirements, gauge, needle sizes, and designer info.
- `GET /patterns/{id}/projects.json`: Community projects made from this pattern.

### Pattern Sources & Categories
- `GET /pattern_sources/search.json`: Search books, magazines, and websites.
- `GET /pattern_sources/{id}.json`: Detailed view of a pattern book/source and its pattern list.
- `GET /pattern_categories/list.json`: Hierarchical taxonomy of pattern categories.

---

## Related
- [[pattern-model]]
- [[project-model]]
- [[needle-model]]
- [[api-search]]
- [[api-projects-and-queue]]
