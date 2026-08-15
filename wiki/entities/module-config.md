---
title: Module - Config
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [stashstats, config, auth, security]
sources: [src/stashstats/config.py]
confidence: high
---

# Module: `stashstats.config`

The `config.py` module defines the centralized application configuration using `pydantic-settings`. It reads values from `.env` or system environment variables with a `RAVELRY_` prefix.

## Primary Class: `Settings`

```python
class Settings(BaseSettings):
    access_key: str
    personal_key: SecretStr
    base_url: str = "https://api.ravelry.com"
    timeout_seconds: float = 15.0
```

### Environment Variables
| Variable | Type | Default | Description |
|---|---|---|---|
| `RAVELRY_ACCESS_KEY` | `str` | *Required* | Basic Auth username. |
| `RAVELRY_PERSONAL_KEY` | `SecretStr` | *Required* | Basic Auth password (hidden in repr). |
| `RAVELRY_API_BASE_URL` | `str` | `https://api.ravelry.com` | Target API host. |
| `RAVELRY_REQUEST_TIMEOUT` | `float` | `15.0` | Request timeout in seconds. |

### Properties & Helpers
- **`auth_tuple`**: Returns `(access_key, personal_key.get_secret_value())` ready for consumption by HTTP Basic Auth handlers.
- **`settings`**: A module-level singleton instance loaded once at startup.

## Cross-References
- [[codebase-architecture]]: Package module hierarchy.
- [[auth-and-permissions]]: Ravelry API authentication protocol details.
- [[module-client]]: Consumes `settings` for request authentication.
