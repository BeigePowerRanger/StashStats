---
title: Common Sub-Models
created: 2026-08-18
updated: 2026-08-18
type: entity
tags: [model, stashstats, pagination]
sources: [raw/articles/ravelry-api-reference.md, src/stashstats/models/common.py]
confidence: high
---

# Common Sub-Models

Shared Pydantic domain models supporting API pagination, image references, fiber definitions, and yarn classification across Ravelry datasets.

## Shared Data Structures (`stashstats.models.common`)

### 1. `Paginator`
Pagination metadata returned by search and list endpoints:
- `page` (`int`): Current 1-indexed page number.
- `page_size` (`int`): Items per page.
- `page_count` (`int`): Total pages available.
- `last_page` (`int`): Index of the last page (automatically synchronized via validator).
- `results` (`int`): Total matching records.

### 2. `Photo`
Asset metadata for photos attached to stash entries, projects, and yarns:
- `id` (`int`): Photo primary key.
- `sort_order` (`int | None`): Image sequence index.
- `user_id` (`int | None`): Creator ID.
- URL variants: `square_url`, `small_url`, `medium_url`, `medium2_url`, `thumbnail_url`, `small2_url`.
- `caption` (`str | None`): Image caption text.

### 3. `FiberType` & `YarnFiber`
Material composition descriptors:
- `FiberType`: ID, name, and animal/plant/synthetic category flags.
- `YarnFiber`: Fiber type reference paired with percentage allocation (0-100%).

### 4. `YarnWeight`
Standard yarn thickness and gauge classification:
- `id` (`int`): Weight identifier (0-7 standard crafting spectrum).
- `name` (`str`): Common weight label (e.g. Lace, Fingering, Sport, DK, Worsted, Bulky).
- `ply` (`str | None`): Traditional ply descriptor (e.g. 4 ply, 8 ply).
- `knit_gauge` (`str | None`), `crochet_gauge` (`str | None`): Standard tension guidelines.

### 5. `YarnCompany`
Manufacturer or indie dyer entity:
- `id` (`int`): Company ID.
- `name` (`str`): Brand name.
- `permalink` (`str`): URL slug.
- `url` (`str | None`): Official web link.

---

## Related
- [[yarn-model]]
- [[stash-model]]
- [[project-model]]
- [[pattern-model]]
- [[paginator-model]]
- [[api-reference-data]]
