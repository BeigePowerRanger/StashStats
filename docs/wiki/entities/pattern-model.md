---
title: Pattern Data Model
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [model, pattern, craft]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Pattern Data Model

Represents a knitting, crochet, weaving, or machine-knitting design pattern.

## Core Schema Fields

| Field Name | Type | Description |
|---|---|---|
| `id` | Integer | Pattern unique ID |
| `name` | String | Pattern title |
| `pattern_author` | Object | Designer details (id, name, permalink) |
| `craft` | Object | Craft classification (Knitting, Crochet, Weaving, Machine Knitting, Loom Knitting) |
| `pattern_categories` | Array | Hierarchical categories (e.g. Clothing -> Sweater -> Pullover) |
| `yardage` / `yardage_max` | Integer | Required yardage range |
| `yarn_weight` | Object | Target yarn weight |
| `gauge` | Float | Stitches per gauge divisor |
| `gauge_divisor` | Integer | Measurement span (inches) |
| `gauge_description`| String | Gauge details and stitch pattern |
| `needle_sizes` | Array | Recommended [[needle-model]] sizes |
| `packs` | Array | Suggested yarn packs & quantities |
| `rating_average` | Float | Community rating |
| `difficulty_average`| Float | Difficulty score (1.0 = Piece of Cake, 10.0 = Hard) |
| `downloadable` | Boolean | True if digital PDF available via Ravelry |
| `free` | Boolean | True if free pattern |

---

## Related
- [[api-patterns-and-sources]]
- [[project-model]]
- [[yarn-model]]
- [[needle-model]]
