---
title: Projects and Queue API
created: 2026-08-14
updated: 2026-08-18
type: entity
tags: [endpoint, project, stash, api-reference]
sources: [raw/articles/ravelry-api-reference.md, live-audit]
confidence: verified
---

# Projects and Queue API

Methods for querying and managing knitting/crochet project records, queued patterns, and linked stash allocations.

## Endpoints

### Projects

#### 1. List Projects (`GET /people/{username}/projects/list.json`)
- **Query Parameters**:
  - `page`: Page index (default: `1`).
  - `page_size`: Results per page (default: `25`, max: `100`).
  - `status`: Filter by project status (e.g. `in-progress`, `finished`, `hibernating`, `frogged`).
  - `craft`: Filter by craft (`crochet`, `knitting`, `weaving`, `spinning`).
- **Response Envelope**: `{"projects": [ProjectListResult], "paginator": Paginator}`
- **Common Project Fields**: `id`, `name`, `status_name`, `progress`, `craft_name`, `started`, `completed`, `rating`, `pattern_name`, `first_photo`, `tag_names`.

#### 2. Project Details (`GET /projects/{username}/{id}.json`)
- **CRITICAL ROUTING ASYMMETRY**: Project detail endpoint is rooted at `/projects/{username}/{id}.json`, NOT `/people/{username}/projects/{id}.json` (which returns empty 404/decode error).
- **Response Envelope**: `{"project": Project, "comments": [Comment]}`
- **Linked Stash Packs**: `project.packs` contains allocated yarn packs (`Pack`), showing `stash_id`, `yarn_id`, `skeins`, `total_yards`, `total_grams`, `colorway`, and `dye_lot`.

#### 3. Mutation Endpoints
- `POST /projects/{username}/create.json`: Create project record.
- `POST /projects/{username}/{id}.json`: Update progress, status, photos, notes, or yarn packs.
- `DELETE /projects/{username}/{id}.json`: Delete project.

### Queued Projects
- `GET /people/{username}/queue/list.json`: List user's queued projects and planned yarn pairings.
  - **Envelope**: `{"queued_projects": [QueuedProject], "paginator": Paginator}`
- `POST /people/{username}/queue/create.json`: Add pattern to queue.
- `POST /people/{username}/queue/reorder.json`: Reorder queue priority.

---

## Related
- [[project-model]]
- [[stash-model]]
- [[pattern-model]]
- [[pack-model]]
- [[input-objects-and-post-data]]
- [[api-stash]]

