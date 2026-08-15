---
title: Projects and Queue API
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, project, stash]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Projects and Queue API

Methods for managing knitting/crochet project records, queued projects, and linking stash yarns to projects.

## Endpoints

### Projects
- `GET /people/{username}/projects/list.json`: List user's projects with status, craft, and dates.
- `GET /projects/{username}/{id}.json`: Full project record including used stash packs, needles, and progress notes.
- `POST /projects/{username}/create.json`: Create a new project.
- `POST /projects/{username}/{id}.json`: Update project progress, rating, completion status, or attached stash.
- `DELETE /projects/{username}/{id}.json`: Delete a project record.

### Queued Projects
- `GET /people/{username}/queue/list.json`: User's queued projects and planned yarn pairings.
- `POST /people/{username}/queue/create.json`: Add pattern to queue.
- `POST /people/{username}/queue/reorder.json`: Reorder queue priority.

---

## Related
- [[project-model]]
- [[stash-model]]
- [[pattern-model]]
- [[input-objects-and-post-data]]
- [[api-stash]]
