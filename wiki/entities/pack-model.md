---
title: Pack and Colorway Allocation Model
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [model, stash, yarn]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Pack and Colorway Allocation Model

The `Pack` object represents a specific batch or grouping of skeins within a stash or project entry.

## Core Schema Fields

| Field Name | Type | Description |
|---|---|---|
| `id` | Integer | Pack ID |
| `stash_id` | Integer | Parent [[stash-model]] ID |
| `yarn_id` | Integer | Associated [[yarn-model]] ID |
| `colorway_name` | String | Name of colorway |
| `color_family_id` | Integer | Associated color family |
| `dye_lot` | String | Dye lot identifier |
| `skeins` | Float | Number of skeins in this pack |
| `grams` | Float | Weight in grams |
| `yards` | Float | Yardage |
| `meters` | Float | Meterage |
| `shop_name` | String | Store where purchased |
| `total_paid` | Float | Purchase cost |
| `currency` | String | ISO Currency code (USD, EUR, GBP, etc.) |

---

## Related
- [[stash-model]]
- [[colorway-model]]
- [[yarn-model]]
