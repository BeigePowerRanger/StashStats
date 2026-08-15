---
title: Codebase Architecture
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [stashstats, client, data-pipeline, model]
sources: [pyproject.toml, src/stashstats/]
confidence: high
---

# Codebase Architecture

StashStats is structured as a modern Python 3.12+ package managed by `uv` using a standard `src/` layout.

```text
2Stash2Stats/
├── .env                      # Active credentials (gitignored)
├── .env.example              # Template environment variables
├── pyproject.toml            # Project build definition & dependencies
├── src/
│   └── stashstats/
│       ├── __init__.py       # Public package API exports
│       ├── config.py         # [[module-config]]: Pydantic Settings & env loading
│       ├── exceptions.py     # [[module-exceptions]]: Typed API error hierarchy
│       ├── auth.py           # [[module-auth]]: Credential verification models
│       ├── base.py           # [[module-client]]: Base synchronous HTTP request engine (BaseAPIClient)
│       ├── client.py         # [[module-client]]: High-level synchronous RavelryClient
│       ├── models/           # Typed Pydantic data schemas
│       │   ├── __init__.py   # Model package exports
│       │   ├── common.py     # [[paginator-model]]: Paginator, Photo, PersonalAttributes, YarnCompany
│       │   ├── yarn.py       # [[yarn-model]]: Yarn, YarnFiber, FiberType, Colorway, YarnSearchResponse
│       │   ├── stash.py      # [[stash-model]]: StashItem, Pack, StashStatus, StashSearchResponse
│       │   ├── history.py    # StashHistory, StashHistoryEntry (Quantity timeline models)
│       │   └── reference.py  # [[api-reference-data]]: ColorFamily, YarnWeightReference, FiberCategory
│       └── dev.py            # Development & interactive prototyping sandbox
└── wiki/                     # [[SCHEMA|LLM Knowledge Wiki]] & [[index|Index]]
```

## Core Modules
- **[[module-config]]**: Loads configuration from `.env` using `pydantic-settings`. Exposes module-level `settings` instance and `auth_tuple`.
- **[[module-exceptions]]**: Maps Ravelry HTTP status codes (401, 403, 404, 429, 5xx) to typed Python exceptions.
- **[[module-auth]]**: Provides `RavelryAuthVerifier` and `AuthVerificationResult` for validating user credentials against `GET /current_user.json`.
- **[[module-client]]**: Provides synchronous `BaseAPIClient` in `base.py` and domain client `RavelryClient` (`client.py`).
- **Models (`models/`)**: Strongly typed Pydantic models for API responses:
  - `common.py`: `Paginator`, `Photo`, `PersonalAttributes`
  - `yarn.py`: `YarnWeight`, `YarnSearchResult`, `YarnSearchResponse`
  - `stash.py`: `StashItem`, `Pack`, `StashStatus`, `StashYarn`, `YarnCompany`, `StashListResponse`

## Conventions
- **Configuration & Typing**: All configuration and data schemas use Pydantic `BaseModel` and `BaseSettings`.
- **Client Strategy**: Pure synchronous execution (`RavelryClient`) with connection pooling for lean architecture.
- **Documentation**: Parameter and attribute docstrings are placed directly under definitions rather than using inline `Field(description=...)`.
- **Packaging**: Managed with `uv`, adhering to PEP 621.
- **Journaling**: Daily development changelogs are tracked in [[2026-08-14|Daily Diary]] entries using Caveman Lite format.
