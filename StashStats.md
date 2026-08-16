# StashStats



## User Notes

- [-] it seems like pydantic BaseModel was implemented just because I told it to, there doesn't seem to be any actual validation going on because almost everything is `x` | None = None
   - I think this is my biggest issue right now honestly  

## Overview

StashStats is being rebuilt from the ground up as a modern Python application to interact with and analyze data from the Ravelry API.

- **UI & Functional Specification**: see [[web-app-specification]] for visual layout, component hierarchy, and supported user capabilities.
- **Knowledge Wiki**: see [[index|Wiki Index]] for complete API docs, endpoints, and schema models.
- **Development Diary**: see [[2026-08-16|Daily Diary]] for chronological changelogs of work done.

## Tech Stack & Tooling

- **Language / Runtime**: Python 3.12+
- **Project & Package Manager**: `uv` + `pyproject.toml`
- **HTTP Client**: `httpx` (supports sync and async client workflows, default timeouts, HTTP/2)
- **Configuration & Validation**: `pydantic-settings` (type-safe configuration loaded from `.env`)
- **Code Quality & Testing**: `pytest`, `pytest-asyncio`, `ruff`

## API Integration

### Authentication

Official documentation details: see \[\[API Auth]].

- **Method**: HTTP Basic Auth (Personal Account Access)
  - **Username**: Access Key (`RAVELRY_ACCESS_KEY`)
  - **Password**: Personal Key (`RAVELRY_PERSONAL_KEY`)
  - **Endpoint Base URL**: `https://api.ravelry.com`
- **Configuration Source**: Environment variables via `.env` file (with `.env.example` template provided).

## Planned Project Structure

```text
2Stash2Stats/
├── .env.example              # Template for Ravelry API credentials
├── .gitignore                # Ignoring .env, .venv, build/cache files
├── pyproject.toml            # Project metadata, dependencies, tool configs
├── README.md
├── src/
│   └── stashstats/
│       ├── __init__.py
│       ├── config.py         # Loads and validates settings via Pydantic
│       ├── auth.py           # HTTP Basic Auth handlers & helpers
│       └── client.py         # Ravelry API client using httpx
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── test_auth.py          # Unit & integration tests for auth and client
```

## Implementation Roadmap

1. **Phase 1: Project Initialization & Environment Setup**
   - Initialize project with `uv` and configure `pyproject.toml`.
   - Setup `.gitignore` and `.env.example`.
2. **Phase 2: Configuration & Authentication Module**
   - Implement `config.py` using `pydantic-settings`.
   - Implement `auth.py` and `client.py` using `httpx`.
   - Write tests verifying authentication headers and endpoint connectivity (e.g. `/current_user.json`).
3. **Phase 3: Core API Endpoints & Data Models**
   - Stash querying, pagination, and data schemas.
