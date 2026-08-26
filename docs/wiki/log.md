# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, archive, delete
> When this file exceeds 500 entries, rotate: rename to log-YYYY.md, start fresh.

## [2026-08-14] create | Wiki initialized
- Domain: Ravelry API Documentation & StashStats Architecture
- Structure created with SCHEMA.md, index.md, log.md

## [2026-08-14] ingest | Ravelry API Complete Documentation
- Ingested source `StashDraft.md` to `raw/articles/ravelry-api-reference.md`
- Created 5 Concept pages (`concepts/`)
- Created 11 API Endpoint Entity pages (`entities/`)
- Created 11 Data Model Entity pages (`entities/`)
- Verified bidirectional wikilinks, index completeness, and frontmatter taxonomy compliance.

## [2026-08-14] update | Added Daily Development Diary requirement to schema
- Updated `SCHEMA.md` with explicit rules and frontmatter schema for maintaining daily development diaries in `wiki/journal/YYYY-MM-DD.md`.
- Created initial diary entry `wiki/journal/2026-08-14.md` documenting all project inception, scaffolding, auth implementations, and live API verifications.
- Updated `wiki/index.md` with the new Journal section.

## [2026-08-14] create | Ingested Codebase Architecture & Modules
- Added [[codebase-architecture]] covering project directory layout and conventions.
- Added module entities: [[module-config]], [[module-auth]], [[module-client]], and [[module-exceptions]].
- Updated [[index|Wiki Index]] with new StashStats Codebase & Architecture section.

## [2026-08-15] update | API Pack Findings & Rules
- Created .agents/rules/stashstats.md to persist three key workflow rules: API-first design, delaying deduplication for Pandas, and saving deferred plans to plans/.
- Added pack observation history plan to plans/.
- Documented findings that Ravelry Pack records are append-only but lack native timestamps.
- Updated 2026-08-15 daily journal with these findings and decisions.

## [2026-08-16] create | Web Application Specification Extracted
- Created [[web-app-specification]] in `concepts/` defining all UI appearances, view layouts, components, and supported functionalities from legacy StashStats.
- Updated [[index|Wiki Index]] and created daily diary [[2026-08-16]].

## [2026-08-17] create | Daily Development Diary
- Created `journal/2026-08-17.md` tracking diagnosis and batch fix planning for 5 core issues in StashStats.
- Updated [[index|Wiki Index]] with journal entry.

## [2026-08-18] create | Daily Development Diary
- Created `journal/2026-08-18.md` tracking diagnosis and fix for modal usage persistence to Ravelry API and state sync.
- Updated [[index|Wiki Index]] with journal entry.

## [2026-08-18] update | Full Live Ravelry API Audit & Schema Verification
- Executed systematic audit script across 21 live Ravelry API endpoints using `KMLadyBugCrochets` account.
- Clarified and resolved critical endpoint routing asymmetries (e.g. `/projects/{username}/{id}.json` vs `/people/{username}/projects/list.json`).
- Documented root response envelope for `GET /yarns/{id}.json?include=colorways`.
- Documented list vs detail payload distinctions for Stash items.
- Added Project & Queue Pydantic models (`src/stashstats/models/project.py`) with unit tests.
- Enhanced entity documentation: [[api-stash]], [[api-yarns-and-companies]], [[api-projects-and-queue]], [[api-reference-data]], [[stash-model]], [[colorway-model]].

## [2026-08-18] lint | Wiki Synchronization & Cross-Link Audit
- Created [[common-models]] (`entities/common-models.md`) documenting shared `Paginator`, `Photo`, `FiberType`, `YarnWeight`, `YarnCompany`.
- Created [[history-model]] (`entities/history-model.md`) documenting `StashHistory` and `StashHistoryEntry` dual-write persistence.
- Created [[consumption-velocity-analytics]] (`concepts/consumption-velocity-analytics.md`) documenting velocity formulas and horizon projections.
- Updated [[project-model]] and [[codebase-architecture]] with web components, callbacks, and latest Pydantic structures.
- Resolved broken wikilinks in [[auth-and-permissions]] and [[api-people-and-current-user]].
- Validated wiki health: 36 content pages (45 total md files including journals/schema/index), 0 broken links, 0 orphan pages, 100% index completeness.

## [2026-08-26] lint | Tag taxonomy reconciliation & health audit (0 errors, 1 warning)
- Ran comprehensive wiki lint across 41 content pages, schema, index, log, and raw sources.
- 0 broken wikilinks, 0 orphan pages, 100% index completeness.
- Reconciled and expanded Tag Taxonomy in `SCHEMA.md` to cover UI, architecture, protocol, and domain model tags.
- Verified raw source hash integrity (0 drift against `raw/articles/ravelry-api-reference.md`).
- Flagged `concepts/web-app-specification.md` (373 lines) as candidate for future modular split.
- Synchronized `index.md` header page count (41 content pages).


