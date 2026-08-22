---
title: People and Current User API
created: 2026-08-14
updated: 2026-08-18
type: entity
tags: [endpoint, user, auth]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# People and Current User API

Endpoints for retrieving profile data, verifying authenticated user identity, and social connections.

## Endpoints

- `GET /current_user.json`: Returns the [[user-model]] for the currently authenticated credentials. Key endpoint for initial connection verification in [[codebase-architecture|StashStats]].
- `GET /people/{username}.json`: Public profile for a user.
- `POST /people/{username}.json`: Update profile info (requires `profile-write` scope).
- `GET /people/{username}/friends/list.json`: List user's friends and activity feeds.
- `GET /people/{username}/favorites/list.json`: List bookmarked/favorited patterns, projects, and yarns.

---

## Related
- [[user-model]]
- [[auth-and-permissions]]
- [[api-app-and-config]]
- [[api-stash]]
