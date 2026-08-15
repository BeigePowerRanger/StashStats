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

