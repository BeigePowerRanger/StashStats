---
name: api-cache-resilience
description: Guidelines for managing external API integration, token caching, rate-limiting, exponential backoff, and local database fallback strategies.
risk: safe
source: community
date_added: "2026-06-12"
---

# API Integration & Cache Resilience Guidelines

Use this skill when implementing or modifying API clients, external integrations, caching strategies, or background synchronizations.

## Use this skill when

- Integrating with third-party APIs (e.g. Ravelry API)
- Implementing or tuning caching strategies (e.g. SQLite cache, Redis cache)
- Handling rate limits or HTTP error states (429, 5xx)
- Managing authentication tokens, credentials, and session refresh logic

## Integration Best Practices

### 1. Robust Caching & Fallbacks
- Cache remote API responses locally (SQLite, JSON, or Redis) with a clear time-to-live (TTL).
- Query the local cache first before calling the remote API.
- Implement a fallback mechanism: if the external API is offline or rate-limited, serve stale cached data to the user rather than crashing.

### 2. Rate-Limiting & Backoff
- Respect rate limit headers returned by the API (e.g. `X-RateLimit-Limit`, `X-RateLimit-Remaining`).
- Use exponential backoff with jitter when retrying failed requests.
- Avoid aggressive retry loops that can lead to permanent IP blocking.

### 3. Connection and Request Lifecycles
- Always configure strict connection and read timeouts on HTTP requests. Never allow requests to hang indefinitely.
- Reuse HTTP client sessions (e.g., using `requests.Session()` in Python) to leverage connection pooling and keep-alive headers.

### 4. Secret & Token Management
- Never hardcode API keys, secrets, or bearer tokens in code.
- Retrieve secrets from environment variables or secure configuration managers.
- Check token expiration times locally before sending requests, and proactively refresh expired tokens using OAuth refresh flows.
