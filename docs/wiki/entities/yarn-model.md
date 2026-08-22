---
title: Yarn Data Model
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [model, yarn, fiber]
sources: [raw/articles/ravelry-api-reference.md, src/stashstats/models/yarn.py]
confidence: high
---

# Yarn Data Model

Represents a commercial or hand-dyed yarn base in Ravelry's database.

## Core Schema Fields (`Yarn`)

| Field Name | Type | Description |
|---|---|---|
| `id` | `Integer` | Primary key of yarn database record |
| `name` | `String` | Commercial yarn name (e.g. "Rios", "Silk Garden") |
| `permalink` | `String` | URL slug for the yarn |
| `yarn_company_name` | `String` | Brand / Dyer name |
| `yarn_company` | `YarnCompany` | Manufacturer details ([[common-models]]) |
| `yarn_weight` | `YarnWeight` | Weight classification (e.g. Worsted, Sport, Fingering) |
| `grams` | `Float` | Unit skein weight in grams |
| `yardage` | `Float` | Unit skein length in yards |
| `texture` | `String` | Plies and spin construction (e.g. "plied", "singles", "chainette") |
| `gauge_description`| `String` | Human-readable gauge summary |
| `machine_washable` | `Boolean` | Care instruction flag |
| `discontinued` | `Boolean` | Whether production has ceased |
| `rating_average` | `Float` | Community rating (1.0 to 5.0) |
| `rating_count` | `Integer` | Total community reviews |
| `yarn_fibers` | `list[YarnFiber]` | Fiber composition percentage breakdown |
| `photos` | `list[Photo]` | Gallery photo assets |

## Fiber Composition Sub-Models
- **`FiberType`**: Categorizes fiber source (`animal_fiber`, `synthetic`, `vegetable`) and naming (`Merino`, `Silk`, `Nylon`).
- **`YarnFiber`**: Pairs a `FiberType` with its composition percentage (e.g. 100% Merino).
- **`Colorway`**: Commercial colorway identifier and optional `color_family_id`.

## Response Envelopes
- `YarnSearchResponse`: `{"paginator": Paginator, "yarns": list[YarnSearchResult]}`
- `YarnDetailResponse`: `{"yarn": Yarn}`

---

## Related
- [[stash-model]]
- [[api-yarns-and-companies]]
- [[colorway-model]]
- [[api-reference-data]]
- [[module-client]]
