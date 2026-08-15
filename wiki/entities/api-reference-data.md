---
title: Reference Data API (Colors, Fibers, Weights, Needles)
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, model, yarn]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Reference Data API (Colors, Fibers, Weights, Needles)

Static and semi-static taxonomy endpoints used to normalize stash and pattern data.

## Endpoints

- `GET /color_families.json`: Master list of color families (e.g. Red, Blue, Neutral, Multi).
- `GET /fiber_categories.json`: Categories of fiber (e.g. Animal, Plant, Synthetic).
- `GET /fiber_attributes.json`: Specific fiber types (e.g. Merino, Silk, Cashmere, Acrylic).
- `GET /yarn_weights.json`: Standard yarn weight classifications (Lace, Fingering, Sport, DK, Worsted, Bulky, Super Bulky).
- `GET /needles/sizes.json`: Knitting needle and crochet hook metric and US sizes.

> [!TIP]
> These endpoints do not require authentication and change very infrequently. Cache responses locally for up to 24 hours as described in [[etags-and-caching]].

---

## Related
- [[etags-and-caching]]
- [[yarn-model]]
- [[needle-model]]
- [[colorway-model]]
