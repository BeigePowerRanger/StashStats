---
title: User Data Model
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [model, user, auth]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# User Data Model

Represents a Ravelry user account and identity.

## Core Schema Fields

| Field Name | Type | Description |
|---|---|---|
| `id` | Integer | Unique user ID |
| `username` | String | Ravelry login username / permalink |
| `photo_url` | String | Avatar image URL |
| `large_photo_url` | String | High-res avatar image URL |
| `location` | String | User location text |
| `about_me` | String | User bio |
| `fav_curator` | Boolean | True if user is a featured favorites curator |
| `designer` | Boolean | True if user has published designs |
| `pattern_author` | Object | Designer profile record if applicable |

---

## Related
- [[api-people-and-current-user]]
- [[auth-and-permissions]]
- [[stash-model]]
- [[project-model]]
