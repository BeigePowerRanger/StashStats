---
title: Module - Auth
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [stashstats, auth, security, client]
sources: [src/stashstats/auth.py]
confidence: high
---

# Module: `stashstats.auth`

The `auth.py` module encapsulates credential validation and authentication status reporting for the Ravelry API.

## Primary Classes

### 1. `AuthVerificationResult` (Pydantic `BaseModel`)
Structured outcome of a credential check against `GET /current_user.json`:
- `valid: bool`: `True` if credentials authenticate successfully.
- `username: str | None`: Ravelry username if valid.
- `user_id: int | None`: Numeric Ravelry account ID.
- `photo_url: str | None`: User avatar URL if present.
- `status_code: int | None`: HTTP error code (e.g. 401, 403) on failure.
- `error: str | None`: Error summary message.
- `details: Any | None`: Raw payload response from server on failure.

### 2. `RavelryAuthVerifier` (Pydantic `BaseModel`)
Executes an active check against the [[api-people-and-current-user]] endpoint:

```python
verifier = RavelryAuthVerifier()
result = verifier.verify_credentials()
if result.valid:
    print(f"Authenticated as {result.username}")
```

## Cross-References
- [[codebase-architecture]]: StashStats module structure.
- [[module-config]]: Supplies API keys and base URL.
- [[auth-and-permissions]]: Ravelry authentication specification.
- [[api-people-and-current-user]]: `/current_user.json` endpoint specification.
