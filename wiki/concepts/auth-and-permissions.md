---
title: Authentication and Permissions
created: 2026-08-14
updated: 2026-08-14
type: concept
tags: [auth, oauth, permissions, security]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Authentication and Permissions

The Ravelry API provides multiple authentication mechanisms depending on application architecture, scope, and user model.

## Authentication Methods

### 1. HTTP Basic Auth: Personal Account Access
- **Credentials**: `username` = Access Key, `password` = Personal Key.
- **Scope**: Full permissions to the associated Ravelry personal account.
- **Use Case**: Personal scripts, local analytics, CLI tools, and single-user apps like [[StashStats]].
- **SSL Required**: Yes (HTTPS required; HTTP requests fail with `403 Forbidden`).
- **Example**:
  ```bash
  curl -u access_key:personal_key https://api.ravelry.com/current_user.json
  ```

### 2. HTTP Basic Auth: Read-Only Access
- **Credentials**: Read-only username and password from app credentials.
- **Scope**: Public, unauthenticated endpoints only (e.g. [[api-reference-data]], [[api-yarns-and-companies]]).

### 3. OAuth 2.0
- **Flow**: Authorization Code Grant with Client ID & Client Secret passed via HTTP Basic Auth header (`Authorization: Basic base64(id:secret)`).
- **Endpoints**:
  - Auth URL: `https://www.ravelry.com/oauth2/auth`
  - Token URL: `https://www.ravelry.com/oauth2/token`
- **Token Lifespan**: 24 hours. Request `offline` scope for refresh token capability.
- **Use Case**: Multi-user web applications where users authenticate via Ravelry.

### 4. OAuth 1.0a (Legacy)
- **Endpoints**: `/oauth/request_token`, `/oauth/access_token`, `/oauth/authorize`.
- Tokens are long-lived but revocable.

---

## OAuth Scopes (Permissions)

Scopes are space-delimited parameters sent during token authorization:

| Scope | Description | Associated Endpoints |
|---|---|---|
| `offline` | Standard OAuth 2.0 refresh token access | [[auth-and-permissions]] |
| `deliveries-read` | Purchased / gifted digital items | [[api-library-and-deliveries]] |
| `forum-write` | Create, edit, and delete forum posts | [[api-forums-and-messages]] |
| `library-pdf` | Download PDFs from user library | [[api-library-and-deliveries]] |
| `profile-write` | Update user profile info | [[api-people-and-current-user]] |
| `patternstore-read` | Enumerate pattern stores & products | [[api-carts-and-stores]] |
| `message-read` | Private messages (limited access) | [[api-forums-and-messages]] |
| `profile-only` | Minimal scope: `/current_user.json` only | [[api-people-and-current-user]] |
| `carts-only` | Minimal scope: `/carts/*.json` only | [[api-carts-and-stores]] |

---

## Related
- [[http-status-codes-and-errors]] (Handling `401 Unauthorized` and `403 Forbidden`)
- [[input-objects-and-post-data]]
- [[api-people-and-current-user]]
- [[api-app-and-config]]
- [[stash-model]]
