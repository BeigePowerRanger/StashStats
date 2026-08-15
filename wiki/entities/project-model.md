---
title: Project Data Model
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [model, project, stash]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Project Data Model

Represents an individual user's crafted project instance.

## Core Schema Fields

| Field Name | Type | Description |
|---|---|---|
| `id` | Integer | Project ID |
| `name` | String | Project title given by user |
| `pattern_id` | Integer | Linked [[pattern-model]] ID |
| `craft_id` | Integer | Craft type ID (Knitting, Crochet, etc.) |
| `status_name` | String | Status (`In progress`, `Finished`, `Hibernating`, `Frogged`) |
| `progress` | Integer | Percent completed (0 to 100) |
| `rating` | Integer | User rating of pattern experience |
| `started` | String | Date started (YYYY-MM-DD) |
| `completed` | String | Date completed (YYYY-MM-DD) |
| `packs` | Array | Array of [[pack-model]] allocations from stash |
| `needle_sizes` | Array | Needles/hooks used for this project |
| `size_name` | String | Pattern size knitted/crocheted |
| `made_for` | String | Recipient of project |
| `notes` | String | Project notes and modifications |

---

## Related
- [[api-projects-and-queue]]
- [[stash-model]]
- [[pattern-model]]
- [[needle-model]]
