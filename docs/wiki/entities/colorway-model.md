---
title: Colorway and Color Family Model
created: 2026-08-14
updated: 2026-08-18
type: entity
tags: [model, yarn, stash, colorway, api-reference]
sources: [raw/articles/ravelry-api-reference.md, live-audit]
confidence: verified
---

# Colorway and Color Family Model

Colorways represent specific color names, dye numbers, and catalog variations for yarns and fiber.

## Colorway Schema (`Colorway`)

| Attribute | Type | Nullable | Description |
|---|---|---|---|
| `id` | `Integer` | No | Colorway database ID |
| `name` | `String` | Yes | Colorway title/name (may be empty string `""` in community entries) |
| `code` | `String` | Yes | Manufacturer color/dye number (e.g. `"405"`) |
| `yarn_id` | `Integer` | Yes | Associated commercial yarn ID |
| `projects_count` | `Integer` | Yes | Number of projects logged with this colorway |
| `stashes_count` | `Integer` | Yes | Number of stash items logged with this colorway |
| `color_family_id` | `Integer` | Yes | Associated color family ID |

### Validation & Fallback Rules
- Community data frequently has blank `name: ""` with only `code: "405"`.
- Pydantic models automatically format empty names as `#{code}` (or empty string fallback) rather than failing validation.

## Color Families
Standardized Ravelry color categories used for faceted search and visualization:
- Black, Grey, White, Natural/Undyed
- Red, Pink, Orange, Yellow, Green, Blue, Purple
- Brown, Multi-color, Variegated, Self-striping

---

## Related
- [[pack-model]]
- [[stash-model]]
- [[yarn-model]]
- [[api-reference-data]]

