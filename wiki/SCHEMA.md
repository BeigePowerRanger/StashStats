# Wiki Schema

## Domain
Ravelry API Documentation, StashStats Architecture, and Project Development Lifecycle. Covers API protocols, authentication, core models (Stash, Yarn, Pattern, Project, User, Library), endpoints, data engineering patterns, and daily working directory changes.

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `auth-and-permissions.md`, `stash-model.md`). Daily diary entries use ISO date format `YYYY-MM-DD.md` in `journal/`.
- Every wiki page starts with YAML frontmatter.
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page).
- When updating a page, always bump the `updated` date.
- Every new page must be added to `index.md` under the correct section.
- Every action must be appended to `log.md`.

---

## Daily Diary & Working Directory Changelog Requirement

To maintain a continuous record of project evolution, the wiki **mandates maintaining a daily development diary**:

1. **Location**: `wiki/journal/YYYY-MM-DD.md`
2. **Frequency**: Updated on every active working day / session whenever modifications occur in the workspace.
3. **Writing Style**: **Caveman Lite**. No filler words, pleasantries, or hedging. Keep articles and complete sentences. Professional, dense, direct, and technically exact. Preserves all code symbols, file paths, and metrics.
4. **Contents Required per Entry**:
   - **Objectives**: What planned / tackled.
   - **Working Directory Changes**: Exact files added/modified/deleted.
   - **Decisions**: Why tech/architecture choices made.
   - **Discoveries**: API / domain findings.
   - **Next**: Forward priorities.
   - **Cross-References**: `[[wikilinks]]` to concepts, entities, models.

### Daily Diary Frontmatter
```yaml
---
title: Daily Diary - YYYY-MM-DD
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: journal
tags: [diary, journal, dev-log, stashstats]
---
```

---

## Standard Wiki Page Frontmatter
```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary | journal
tags: [from taxonomy below]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high | medium | low
---
```

## Tag Taxonomy
- **Auth & Access**: `auth`, `oauth`, `permissions`, `security`
- **Core Entities**: `model`, `stash`, `yarn`, `pattern`, `project`, `user`, `needle`, `pack`, `colorway`, `library`, `cart`, `forum`, `search`, `app`
- **Protocols & Infra**: `endpoint`, `pagination`, `caching`, `etag`, `cors`, `http-status`, `rate-limits`
- **Application & Development**: `stashstats`, `data-pipeline`, `client`, `diary`, `journal`, `dev-log`

## Page Thresholds
- **Create a page** when an entity or concept is central to the Ravelry ecosystem or API integration.
- **Maintain a daily journal file** for each day development work occurs.
- **Split a page** when it exceeds ~200-250 lines into focused sub-topic pages with cross-links.
- **Maintain bidirectional links** across endpoints, models, concepts, and journal entries.
