---
title: Codebase Architecture
created: 2026-08-14
updated: 2026-08-18
type: entity
tags: [stashstats, client, data-pipeline, model]
sources: [pyproject.toml, src/stashstats/]
confidence: high
---

# Codebase Architecture

StashStats is structured as a modern Python 3.12+ analytics and management application using Dash and Pydantic, managed by `uv` using a standard `src/` layout.

```text
StashStats/
├── .env                      # Active credentials (gitignored)
├── .env.example              # Template environment variables
├── pyproject.toml            # Project build definition & dependencies
├── app.py                    # Main Dash application entrypoint
├── dev.py                    # Dev server runner
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
│       │   ├── common.py     # [[common-models]]: Paginator, Photo, PersonalAttributes, YarnCompany, YarnWeight
│       │   ├── yarn.py       # [[yarn-model]]: Yarn, YarnFiber, FiberType, Colorway, YarnSearchResponse
│       │   ├── stash.py      # [[stash-model]]: StashItem, Pack, StashStatus, StashSearchResponse
│       │   ├── history.py    # [[history-model]]: StashHistory, StashHistoryEntry (Quantity timeline models)
│       │   ├── project.py    # [[project-model]]: ProjectListResult, Project, QueuedProject
│       │   └── reference.py  # [[api-reference-data]]: ColorFamily, YarnWeightReference, FiberCategory
│       └── web/              # [[web-app-specification]]: Dash UI layer
│           ├── app.py        # Dash app initialization & layout composition
│           ├── components/   # UI components (modal, stash, header, search)
│           ├── callbacks/    # Interactive event handlers (modal, search, stash)
│           └── layouts/      # Container and page layouts (main, header)
├── docs/wiki/                # [[SCHEMA|LLM Knowledge Wiki]] & [[index|Index]]
└── tests/                    # Pytest test suite (unit, model, integration, web)
```

## Core Modules & Layers
- **[[module-config]]**: Loads configuration from `.env` using `pydantic-settings`. Exposes module-level `settings` instance and `auth_tuple`.
- **[[module-exceptions]]**: Maps Ravelry HTTP status codes (401, 403, 404, 429, 5xx) to typed Python exceptions.
- **[[module-auth]]**: Provides `RavelryAuthVerifier` and `AuthVerificationResult` for validating user credentials against `GET /current_user.json`.
- **[[module-client]]**: Provides synchronous `BaseAPIClient` in `base.py` and domain client `RavelryClient` (`client.py`).
- **Models (`models/`)**: Strongly typed Pydantic models for API responses:
  - `common.py`: [[common-models]] (`Paginator`, `Photo`, `PersonalAttributes`, `YarnCompany`, `YarnWeight`)
  - `yarn.py`: [[yarn-model]] (`Yarn`, `YarnSearchResult`, `YarnSearchResponse`, `Colorway`)
  - `stash.py`: [[stash-model]] (`StashItem`, `Pack`, `StashStatus`, `StashListResponse`)
  - `history.py`: [[history-model]] (`StashHistory`, `StashHistoryEntry`)
  - `project.py`: [[project-model]] (`ProjectListResult`, `Project`, `QueuedProject`)
  - `reference.py`: [[api-reference-data]] (`ColorFamily`, `YarnWeightReference`, `FiberCategory`)
- **Web (`web/`)**: [[web-app-specification]]:
  - `components/`: Modular Dash UI widgets (`create_stash_modal`, `group_stash_items`, `create_stash_item_row`).
  - `callbacks/`: Dual-write API handlers, search event triggers, and stash mutations.

## Conventions
- **Configuration & Typing**: All configuration and data schemas use Pydantic `BaseModel` and `BaseSettings`.
- **Client Strategy**: Pure synchronous execution (`RavelryClient`) with connection pooling for lean architecture.
- **Documentation**: Parameter and attribute docstrings are placed directly under definitions rather than using inline `Field(description=...)`.
- **Packaging**: Managed with `uv`, adhering to PEP 621.
- **Journaling**: Daily development changelogs are tracked in [[2026-08-18|Daily Diary]] entries using Caveman Lite format.

