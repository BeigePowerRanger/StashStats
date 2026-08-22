---
title: Reference Data API (Colors, Fibers, Weights, Needles, Categories)
created: 2026-08-14
updated: 2026-08-18
type: entity
tags: [endpoint, model, yarn, reference, api-reference]
sources: [raw/articles/ravelry-api-reference.md, live-audit]
confidence: verified
---

# Reference Data API (Colors, Fibers, Weights, Needles, Categories)

Static and semi-static taxonomy endpoints used to normalize stash, yarn, and pattern metadata.

## Endpoints & Schemas

### 1. Color Families (`GET /color_families.json`)
- **Envelope**: `{"color_families": [ColorFamily]}`
- **Schema**: `id: int`, `name: str`, `color: str` (hex code, e.g. `"#FF0000"`), `spectrum_order: int`.

### 2. Yarn Weights (`GET /yarn_weights.json`)
- **Envelope**: `{"yarn_weights": [YarnWeight]}`
- **Schema**: `id: int`, `name: str`, `ply: str | None`, `wpi: str | None`, `knit_gauge: str | None`, `crochet_gauge: str | None`, `min_gauge: float | None`, `max_gauge: float | None`.

### 3. Fiber Categories (`GET /fiber_categories.json`)
- **Envelope**: `{"fiber_categories": [FiberCategory]}`
- **Schema**: `id: int`, `name: str`, `permalink: str`.

### 4. Needle & Hook Sizes (`GET /needles/sizes.json`)
- **Envelope**: `{"needle_sizes": [NeedleSize]}`
- **Schema**: `id: int`, `metric: float`, `us: str | None`, `uk: str | None`, `knitting: bool`, `crochet: bool`.

### 5. Pattern Categories Tree (`GET /pattern_categories/list.json`)
- **Envelope**: `{"pattern_categories": PatternCategoryNode}`
- **Schema**: Root node containing hierarchical `children: list[PatternCategoryNode]` (e.g. `Clothing -> Sweater -> Pullover`).

> [!TIP]
> These reference endpoints change very infrequently. Cache responses locally or in Redis with a 24-hour TTL as detailed in [[etags-and-caching]].

---

## Related
- [[etags-and-caching]]
- [[yarn-model]]
- [[needle-model]]
- [[colorway-model]]
- [[stash-model]]

