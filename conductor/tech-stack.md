# Tech Stack: StashStats

## Core Language & Runtime
- **Python 3.12+**: The primary programming language.

## Package Management & Build
- **uv**: Extremely fast Python package installer and resolver.
- **Hatchling**: The PEP 517 build backend (utilized by uv under the hood).

## Core Libraries
- **Pydantic**: Data validation and settings management.
- **HTTPX**: Fully featured async HTTP client for interacting with the Ravelry API.

## Code Quality & Tooling
- **Black**: The uncompromising Python code formatter.
- **Ruff**: Extremely fast Python linter.

## Infrastructure & Deployment (Planned)
- **Docker & Docker Compose**: Containerization and multi-container orchestration for running the application stack.
- **Redis**: In-memory data store to be used for caching API responses and data.

## Frontend
- **Dash 2.x**: Reactive Python framework for building analytical web applications.
- **Dash Bootstrap Components**: For responsive layout and pre-built UI components using the DARKLY theme.
- **FastAPI**: Underlying ASGI server for handling routing and API endpoints.
