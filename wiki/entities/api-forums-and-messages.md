---
title: Forums and Messages API
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, forum, social]
sources: [raw/articles/ravelry-api-reference.md]
confidence: medium
---

# Forums and Messages API

Endpoints for browsing community boards, reading/writing forum posts, and handling private user messages.

## Endpoints

- `GET /forums/sets.json`: List forum categories and boards.
- `GET /forums/{id}/topics/list.json`: List topics in a forum.
- `GET /topics/{id}.json`: View posts in a thread.
- `POST /forum_posts/create.json`: Post reply (requires `forum-write` scope).
- `GET /messages/list.json`: List private messages (requires `message-read` scope).

---

## Related
- [[forum-models]]
- [[auth-and-permissions]]
- [[user-model]]
