---
title: Project Data Model
created: 2026-08-14
updated: 2026-08-18
type: entity
tags: [model, project, stash]
sources: [raw/articles/ravelry-api-reference.md, src/stashstats/models/project.py]
confidence: high
---

# Project Data Model

Represents a user's crafted project instance and queued project plans in Ravelry.

## Data Structures (`stashstats.models.project`)

### 1. `ProjectListResult` (Summary Model)
Returned in project list endpoints (`GET /people/{username}/projects/list.json`):
- `id` (`int`): Unique project ID.
- `name` (`str`): User project title.
- `status_name` (`str | None`): Status string (`In progress`, `Finished`, `Hibernating`, `Frogged`).
- `progress` (`int`): Completion percentage (0 to 100).
- `craft_name` (`str | None`): Craft category (`Knitting`, `Crochet`, `Weaving`, etc.).
- `pattern_name` (`str | None`): Linked pattern title if associated.
- `started` (`str | None`): Start date string (`YYYY/MM/DD`).
- `completed` (`str | None`): Finish date string (`YYYY/MM/DD`).
- `rating` (`int | None`): User pattern/crafting rating.
- `first_photo` (`Photo | None`): Representative [[common-models|Photo]].
- `tag_names` (`list[str]`): User-assigned tags.

### 2. `Project` (Detailed Model)
Returned in project detail endpoints (`GET /projects/{username}/{id}.json`):
- Extends `ProjectListResult` with:
  - `packs` (`list[Pack]`): Allocated yarn packs and [[stash-model]] records.
  - `photos` (`list[Photo]`): Full gallery photo assets.
  - `notes` (`str | None`), `notes_html` (`str | None`): Project notes.
  - `made_for` (`str | None`): Recipient.
  - `size_name` (`str | None`): Sizing details.

### 3. `QueuedProject`
Returned in user queue list (`GET /people/{username}/queue/list.json`):
- `id` (`int`): Queued entry identifier.
- `name` (`str`): Project / pattern name.
- `sort_order` (`int`): Queue sequence priority.
- `pattern_id` (`int | None`), `pattern_name` (`str | None`): Associated pattern.
- `notes` (`str | None`): Planning notes.

### 4. Response Envelopes
- `ProjectListResponse`: `{"projects": list[ProjectListResult], "paginator": Paginator}`
- `ProjectDetailResponse`: `{"project": Project, "comments": list[dict]}`
- `QueueListResponse`: `{"queued_projects": list[QueuedProject], "paginator": Paginator}`

---

## Related
- [[api-projects-and-queue]]
- [[stash-model]]
- [[pattern-model]]
- [[pack-model]]
- [[needle-model]]
- [[common-models]]

