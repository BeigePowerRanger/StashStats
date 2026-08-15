# Wiki Index

> Content catalog for Ravelry API Documentation & StashStats Architecture.
> Read this first to find relevant pages for any query.
> Last updated: 2026-08-14 | Total pages: 29

## Daily Diary & Journal
- [[2026-08-15]]: Stash Consumption Velocity & Horizon Lifespan Analytics Engine design; created repository `plans/` documentation directory.
- [[2026-08-14]]: Project inception, LLM wiki creation, Python 3.12+ scaffolding with uv, Ravelry auth implementation, stash CRUD, App Data history tracking, MVP data models, and live verification.

## StashStats Codebase & Architecture
- [[codebase-architecture]]: Package structure, `src/stashstats` layout, and conventions.
- [[module-config]]: `stashstats.config` — Pydantic Settings and environment variable loading.
- [[module-auth]]: `stashstats.auth` — Credential verification models and status reporting.
- [[module-client]]: `stashstats.client` — Base HTTP client, sync/async Ravelry API clients.
- [[module-exceptions]]: `stashstats.exceptions` — Custom exception hierarchy and HTTP status dispatching.

## Concepts
- [[auth-and-permissions]]: Authentication protocols (Basic Auth, OAuth 2.0, OAuth 1.0a) and permission scopes.
- [[pagination-and-sorting]]: API pagination mechanics, `sort_` conventions, and `paginator` payload structure.
- [[http-status-codes-and-errors]]: HTTP 4xx/5xx status codes, rate limits, and failure recovery.
- [[etags-and-caching]]: ETag conditional queries and recommended TTLs for reference datasets.
- [[input-objects-and-post-data]]: Payload structures for POST/PUT endpoints (raw JSON vs form-data).

## Entities
### API Endpoints
- [[api-stash]]: User stash query, create, update, and search endpoints.
- [[api-yarns-and-companies]]: Commercial & indie yarn search, colorways, and yarn manufacturers.
- [[api-patterns-and-sources]]: Pattern catalogs, yardage specs, needle sizes, and source publications.
- [[api-projects-and-queue]]: User project progress tracking, craft types, and queued projects.
- [[api-people-and-current-user]]: Authenticated user profile, identity check (`/current_user.json`), and social features.
- [[api-library-and-deliveries]]: Digital PDF library, purchased products, and download tokens.
- [[api-forums-and-messages]]: Community boards, discussion topics, and private messages.
- [[api-search]]: Global multi-entity full-text search.
- [[api-app-and-config]]: Cloud key-value storage and sync for third-party client apps.
- [[api-reference-data]]: Non-authenticated static taxonomies (colors, fibers, weights, needle sizes).
- [[api-carts-and-stores]]: Pattern store checkout and digital delivery integrations.

### Data Models
- [[stash-model]]: Stash entry holding yarn quantities, yardage, packs, photos, and location.
- [[yarn-model]]: Commercial yarn base definition, fiber breakdown, gauge, and weight specs.
- [[pattern-model]]: Design specifications, difficulty ratings, craft, yardage, and needle requirements.
- [[project-model]]: User project crafting instance linked to stash packs and patterns.
- [[user-model]]: Ravelry user profile, designer identity, and account attributes.
- [[needle-model]]: Needle and crochet hook sizing standards (metric, US, UK).
- [[pack-model]]: Batch skein allocation within a stash or project item with dye lot and purchase info.
- [[colorway-model]]: Colorway name and color family classification.
- [[paginator-model]]: Response pagination envelope (`page`, `page_count`, `results`, `last_page`).
- [[cart-and-product-models]]: Commerce models for digital carts, line items, invoices, and PDF downloads.
- [[forum-models]]: Community models for forums, topics, posts, and direct messages.

## Comparisons

## Queries
