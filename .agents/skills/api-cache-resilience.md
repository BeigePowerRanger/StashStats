---
name: api-cache-resilience
description: Guidelines for managing external API integration, token caching, rate-limiting, exponential backoff, and local database fallback strategies.
risk: safe
source: community
date_added: "2026-06-12"
---

# API Integration & Cache Resilience Guidelines

Use when modifying API clients, external integrations, caching strategies, or background syncs.

## Use this skill when

- Integrating with third-party APIs (e.g. Ravelry API)
- Tuning caching strategies (e.g. SQLite cache, Redis cache)
- Handling rate limits or HTTP error states (429, 5xx)
- Managing auth tokens, credentials, session refresh logic

## Integration Best Practices

### 1. Robust Caching & Fallbacks
- Cache remote API responses locally (SQLite, JSON, Redis) with time-to-live (TTL).
- Query local cache before calling remote API.
- Implement fallback: if external API offline or rate-limited, serve stale cached data instead of crashing.

### 2. Rate-Limiting & Backoff
- Respect rate limit headers from API (e.g. `X-RateLimit-Limit`, `X-RateLimit-Remaining`).
- Use exponential backoff with jitter when retrying failed requests.
- Avoid aggressive retry loops causing permanent IP blocking.

### 3. Connection and Request Lifecycles
- Configure strict connection and read timeouts on HTTP requests. Never let requests hang.
- Reuse HTTP client sessions (e.g., `requests.Session()` in Python) to leverage connection pooling and keep-alive headers.

### 4. Secret & Token Management
- Never hardcode API keys, secrets, or bearer tokens in code.
- Retrieve secrets from environment variables or secure configuration managers.
- Check token expiration locally before sending requests. Proactively refresh expired tokens using OAuth refresh flows.
