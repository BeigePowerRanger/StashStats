---
title: Yarns and Yarn Companies API
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, yarn, model, search]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Yarns and Yarn Companies API

Provides search, discovery, and detailed lookup for commercial and indie yarns, fiber compositions, and yarn companies.

## Endpoints

### Yarns
- `GET /yarns/search.json`: Full-text & faceted search for yarns with filters for weight, fiber, company, and ratings.
- `GET /yarns/{id}.json`: Detailed record for a single yarn including weight, fiber breakdown, gauge, yardage, and colorways.
- `GET /yarns/{id}/colorways.json`: List of known colorways for a yarn.
- `GET /yarns/{id}/comments.json`: User comments for a yarn.
- `GET /yarns/{id}/photos.json`: Associated user and official photos.

### Yarn Companies
- `GET /yarn_companies/search.json`: Search yarn manufacturers and indie dyers.
- `GET /yarn_companies/{id}.json`: Information on a specific yarn company and its active yarn lines.
- `GET /yarn_companies/{id}/yarns.json`: All yarns produced by a specific company.

---

## Related
- [[yarn-model]]
- [[stash-model]]
- [[colorway-model]]
- [[api-stash]]
- [[api-search]]
- [[api-reference-data]]
