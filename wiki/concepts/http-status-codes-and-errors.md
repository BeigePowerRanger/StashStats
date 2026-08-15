---
title: HTTP Status Codes and Error Handling
created: 2026-08-14
updated: 2026-08-14
type: concept
tags: [http-status, rate-limits, protocol, security]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# HTTP Status Codes and Error Handling

The Ravelry API communicates request outcomes using standard HTTP status codes.

## Client Error Codes (4xx)

| Status Code | Reason | Resolution Strategy |
|---|---|---|
| `400 Bad Request` | Invalid query parameters, missing required fields, or malformed body. | Verify parameter data types against documentation. |
| `401 Unauthorized` | OAuth token expired or revoked. | Refresh access token using `offline` refresh token or re-authenticate. |
| `402 Payment Required` | Used in digital commerce/pattern store checkouts. | Complete payment flow. |
| `403 Forbidden` | Invalid API keys, non-SSL HTTP connection, or missing scope permissions. | Check SSL/HTTPS usage, API keys, or OAuth scopes. |
| `404 Not Found` | Resource ID does not exist or was deleted. | Handle missing record gracefully. |
| `405 Method Not Allowed` | Incorrect HTTP method (e.g. GET instead of POST). | Verify HTTP verb on endpoint. |
| `413 Request Entity Too Large` | POST body or payload exceeds size limit. | Reduce payload or batch uploads. |
| `429 Too Many Requests` | Rate limit exceeded. | Implement exponential backoff. |

## Server Error Codes (5xx)

| Status Code | Reason | Resolution Strategy |
|---|---|---|
| `500 Internal Server Error` | Server-side bug or unexpected exception. | Retry with backoff or report to Ravelry API team. |
| `503 Service Unavailable` | Maintenance mode or temporary outage. | Retry after delay. |
| `504 Gateway Timeout` | Server took >10 seconds to generate response. | Reduce `page_size` (<= 100) or refine query filters. |

---

## Related
- [[auth-and-permissions]]
- [[pagination-and-sorting]]
- [[etags-and-caching]]
