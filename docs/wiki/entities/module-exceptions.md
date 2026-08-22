---
title: Module - Exceptions
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [stashstats, http-status, client]
sources: [src/stashstats/exceptions.py]
confidence: high
---

# Module: `stashstats.exceptions`

The `exceptions.py` module defines a custom exception hierarchy mapping Ravelry REST API error codes to typed Python exceptions.

## Exception Hierarchy
```text
Exception
└── RavelryAPIError
    ├── RavelryAuthError         # 401 Unauthorized, 403 Forbidden
    ├── RavelryNotFoundError     # 404 Not Found
    ├── RavelryRateLimitError    # 429 Too Many Requests
    └── RavelryServerError       # 5xx Internal Server Errors
```

## Status Code Dispatcher: `raise_for_status_code`
Translates response status codes and attaches response payloads directly to exception instances:

```python
def raise_for_status_code(status_code: int, message: str, response_body: Any | None = None) -> None:
    ...
```

## Cross-References
- [[codebase-architecture]]: Package architecture overview.
- [[http-status-codes-and-errors]]: Official Ravelry API status code specifications.
- [[module-client]]: Invokes exception dispatcher on non-2xx responses.
