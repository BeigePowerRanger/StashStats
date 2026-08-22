---
title: Needle and Tool Data Model
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [model, needle, craft]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Needle and Tool Data Model

Represents knitting needles, crochet hooks, and tools in a user's inventory or pattern specifications.

## Core Schema Fields

| Field Name | Type | Description |
|---|---|---|
| `id` | Integer | Unique needle size ID |
| `metric` | Float | Size in millimeters (e.g. 4.0) |
| `us` | String | US size designation (e.g. "6") |
| `uk` | String | UK size designation (e.g. "8") |
| `crochet` | String | Crochet hook letter designation (e.g. "G-6") |
| `length` | Float | Needle / cord length |
| `needle_type` | Object | Type (`circular`, `straight`, `dpn`, `interchangeable`) |

---

## Related
- [[pattern-model]]
- [[project-model]]
- [[api-reference-data]]
