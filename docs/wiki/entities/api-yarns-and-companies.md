---
title: Yarns and Yarn Companies API
created: 2026-08-14
updated: 2026-08-18
type: entity
tags: [endpoint, yarn, model, search, api-reference]
sources: [raw/articles/ravelry-api-reference.md, live-audit]
confidence: verified
---

# Yarns and Yarn Companies API

Provides search, discovery, and detailed lookup for commercial and indie yarns, fiber compositions, and yarn companies.

## Endpoints

### Yarns

#### 1. Search (`GET /yarns/search.json`)
- **Query Parameters**:
  - `query`: Text query string (e.g. `Malabrigo Rios`, `Bernat`).
  - `sort`: Sorting criteria (`best`, `rating`, `projects`, `name`).
  - `page`: Page index (default: `1`).
  - `page_size`: Results per page (default: `50`, max: `100`).
- **Response Envelope**: `{"yarns": [YarnSearchResult], "paginator": Paginator}`
- **Item Fields**: `id`, `name`, `permalink`, `yarn_company_name`, `grams`, `yardage`, `texture`, `machine_washable`, `min_gauge`, `max_gauge`, `gauge_divisor`, `rating_average`, `rating_count`, `first_photo`.

#### 2. Details (`GET /yarns/{id}.json`)
- **Query Parameters**:
  - `include`: Space or comma-delimited extra sections to include. Supported options: `colorways`, `availability`.
- **Response Envelope**:
  - Default: `{"yarn": Yarn}`
  - With `?include=colorways`: `{"yarn": Yarn, "colorways": [Colorway]}`
  - **CRITICAL ENVELOPE BEHAVIOR**: When `include=colorways` is passed, `colorways` array is placed at the **root response envelope level**, not nested inside `yarn`. Client models must inspect root `colorways` or bind via Pydantic model validator.
- **Colorway Schema**:
  - `id`: Unique colorway ID.
  - `name`: User-facing colorway name (may be empty string `""` in community entries).
  - `code`: Manufacturer dye number or SKU (e.g. `"405"`).
  - `yarn_id`: Parent catalog yarn ID.
  - `projects_count`: Number of projects logged with this colorway.
  - `stashes_count`: Number of stash items logged with this colorway.

### Yarn Companies
- `GET /yarn_companies/search.json`: Search yarn manufacturers and indie dyers.
- `GET /yarn_companies/{id}.json`: Information on a specific yarn company and its active yarn lines.

---

## Related
- [[yarn-model]]
- [[stash-model]]
- [[colorway-model]]
- [[api-stash]]
- [[api-search]]
- [[api-reference-data]]

