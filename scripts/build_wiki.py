#!/usr/bin/env python3
import os
import re
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1] / "docs"
WIKI_DIR = BASE_DIR / "wiki"
RAW_ARTICLES_DIR = WIKI_DIR / "raw" / "articles"
RAW_PAPERS_DIR = WIKI_DIR / "raw" / "papers"
RAW_TRANSCRIPTS_DIR = WIKI_DIR / "raw" / "transcripts"
RAW_ASSETS_DIR = WIKI_DIR / "raw" / "assets"
ENTITIES_DIR = WIKI_DIR / "entities"
CONCEPTS_DIR = WIKI_DIR / "concepts"
COMPARISONS_DIR = WIKI_DIR / "comparisons"
QUERIES_DIR = WIKI_DIR / "queries"

for d in [RAW_ARTICLES_DIR, RAW_PAPERS_DIR, RAW_TRANSCRIPTS_DIR, RAW_ASSETS_DIR, ENTITIES_DIR, CONCEPTS_DIR, COMPARISONS_DIR, QUERIES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# 1. Ingest Raw Source
with open(BASE_DIR / "StashDraft.md", "r", encoding="utf-8") as f:
    draft_content = f.read()

sha256 = hashlib.sha256(draft_content.encode("utf-8")).hexdigest()
raw_source_path = RAW_ARTICLES_DIR / "ravelry-api-reference.md"
raw_frontmatter = f"""---
source_url: https://www.ravelry.com/api
ingested: 2026-08-14
sha256: {sha256}
---
"""
with open(raw_source_path, "w", encoding="utf-8") as f:
    f.write(raw_frontmatter + draft_content)

# 2. SCHEMA.md
schema_content = """# Wiki Schema

## Domain
Ravelry API Documentation & StashStats Architecture. Covers API protocols, authentication, core models (Stash, Yarn, Pattern, Project, User, Library), endpoints, and data engineering patterns for stash analysis.

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `auth-and-permissions.md`, `stash-model.md`)
- Every wiki page starts with YAML frontmatter
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be appended to `log.md`

## Frontmatter
```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [from taxonomy below]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high | medium | low
---
```

## Tag Taxonomy
- **Auth & Access**: `auth`, `oauth`, `permissions`, `security`
- **Core Entities**: `model`, `stash`, `yarn`, `pattern`, `project`, `user`, `needle`, `pack`, `colorway`, `library`, `cart`, `forum`, `search`, `app`
- **Protocols & Infra**: `endpoint`, `pagination`, `caching`, `etag`, `cors`, `http-status`, `rate-limits`
- **Application**: `stashstats`, `data-pipeline`, `client`

## Page Thresholds
- **Create a page** when an entity or concept is central to the Ravelry ecosystem or API integration.
- **Split a page** when it exceeds ~200-250 lines into focused sub-topic pages with cross-links.
- **Maintain bidirectional links** across endpoints, models, and concepts.
"""

with open(WIKI_DIR / "SCHEMA.md", "w", encoding="utf-8") as f:
    f.write(schema_content)

# 3. Create Concepts
concepts = {
    "auth-and-permissions.md": """---
title: Authentication and Permissions
created: 2026-08-14
updated: 2026-08-14
type: concept
tags: [auth, oauth, permissions, security]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Authentication and Permissions

The Ravelry API provides multiple authentication mechanisms depending on application architecture, scope, and user model.

## Authentication Methods

### 1. HTTP Basic Auth: Personal Account Access
- **Credentials**: `username` = Access Key, `password` = Personal Key.
- **Scope**: Full permissions to the associated Ravelry personal account.
- **Use Case**: Personal scripts, local analytics, CLI tools, and single-user apps like [[StashStats]].
- **SSL Required**: Yes (HTTPS required; HTTP requests fail with `403 Forbidden`).
- **Example**:
  ```bash
  curl -u access_key:personal_key https://api.ravelry.com/current_user.json
  ```

### 2. HTTP Basic Auth: Read-Only Access
- **Credentials**: Read-only username and password from app credentials.
- **Scope**: Public, unauthenticated endpoints only (e.g. [[api-reference-data]], [[api-yarns-and-companies]]).

### 3. OAuth 2.0
- **Flow**: Authorization Code Grant with Client ID & Client Secret passed via HTTP Basic Auth header (`Authorization: Basic base64(id:secret)`).
- **Endpoints**:
  - Auth URL: `https://www.ravelry.com/oauth2/auth`
  - Token URL: `https://www.ravelry.com/oauth2/token`
- **Token Lifespan**: 24 hours. Request `offline` scope for refresh token capability.
- **Use Case**: Multi-user web applications where users authenticate via Ravelry.

### 4. OAuth 1.0a (Legacy)
- **Endpoints**: `/oauth/request_token`, `/oauth/access_token`, `/oauth/authorize`.
- Tokens are long-lived but revocable.

---

## OAuth Scopes (Permissions)

Scopes are space-delimited parameters sent during token authorization:

| Scope | Description | Associated Endpoints |
|---|---|---|
| `offline` | Standard OAuth 2.0 refresh token access | [[auth-and-permissions]] |
| `deliveries-read` | Purchased / gifted digital items | [[api-library-and-deliveries]] |
| `forum-write` | Create, edit, and delete forum posts | [[api-forums-and-messages]] |
| `library-pdf` | Download PDFs from user library | [[api-library-and-deliveries]] |
| `profile-write` | Update user profile info | [[api-people-and-current-user]] |
| `patternstore-read` | Enumerate pattern stores & products | [[api-carts-and-stores]] |
| `message-read` | Private messages (limited access) | [[api-forums-and-messages]] |
| `profile-only` | Minimal scope: `/current_user.json` only | [[api-people-and-current-user]] |
| `carts-only` | Minimal scope: `/carts/*.json` only | [[api-carts-and-stores]] |

---

## Related
- [[http-status-codes-and-errors]] (Handling `401 Unauthorized` and `403 Forbidden`)
- [[input-objects-and-post-data]]
- [[api-people-and-current-user]]
- [[api-app-and-config]]
- [[stash-model]]
""",

    "pagination-and-sorting.md": """---
title: Pagination and Sorting
created: 2026-08-14
updated: 2026-08-14
type: concept
tags: [pagination, endpoint, protocol]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Pagination and Sorting

The Ravelry API provides a standardized mechanism for pagination and multi-field sorting across list endpoints.

## Pagination Parameters

Methods that support pagination accept the following query parameters:
- `page`: Result page number to retrieve (1-indexed, default: `1`).
- `page_size`: Number of records per page (default: typically `25` or `50`, max: `100` to `500` depending on endpoint).

### The Paginator Object
Paginated responses include a `paginator` metadata object alongside the result list:
- `page`: Current page number.
- `page_count`: Total number of pages available.
- `page_size`: Number of results requested per page.
- `results`: Total count of matching records across all pages.
- `last_page`: Boolean indicating if this is the final page.

See [[paginator-model]] for schema details.

---

## Sorting Rules

Unless otherwise specified, API calls accepting a `sort` parameter have two conventions:
1. **Multiple Sort Orders**: Space-delimited string of sort keys (e.g. `sort=yarn_name rating`).
2. **Descending / Reversed Sort**: Append an underscore `_` suffix to reverse the sort order (e.g. `sort=created_` for newest first, `name_` for Z-A).

---

## Related
- [[paginator-model]]
- [[api-stash]]
- [[api-patterns-and-sources]]
- [[api-projects-and-queue]]
- [[http-status-codes-and-errors]]
""",

    "http-status-codes-and-errors.md": """---
title: HTTP Status Codes and Error Handling
created: 2026-08-14
updated: 2026-08-14
type: concept
tags: [http-status, rate-limits, protocol, security]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# HTTP Status Codes and Error Handling

The Ravelry API communicates request outcomes using standard HTTP status codes.

## Client Error Codes (4xx)

| Status Code | Reason | Resolution Strategy |
|---|---|---|
| `400 Bad Request` | Invalid query parameters, missing required fields, or malformed body. | Verify parameter data types against documentation. |
| `401 Unauthorized` | OAuth token expired or revoked. | Refresh access token using `offline` refresh token or re-authenticate. |
| `402 Payment Required` | Used in digital commerce/pattern store checkouts. | Complete payment flow. |
| `403 Forbidden` | Invalid API keys, non-SSL HTTP connection, or missing scope permissions. | Check SSL/HTTPS usage, API keys, or OAuth scopes. |
| `404 Not Found` | Resource ID does not exist or was deleted. | Handle missing record gracefully. |
| `405 Method Not Allowed` | Incorrect HTTP method (e.g. GET instead of POST). | Verify HTTP verb on endpoint. |
| `413 Request Entity Too Large` | POST body or payload exceeds size limit. | Reduce payload or batch uploads. |
| `429 Too Many Requests` | Rate limit exceeded. | Implement exponential backoff. |

## Server Error Codes (5xx)

| Status Code | Reason | Resolution Strategy |
|---|---|---|
| `500 Internal Server Error` | Server-side bug or unexpected exception. | Retry with backoff or report to Ravelry API team. |
| `503 Service Unavailable` | Maintenance mode or temporary outage. | Retry after delay. |
| `504 Gateway Timeout` | Server took >10 seconds to generate response. | Reduce `page_size` (<= 100) or refine query filters. |

---

## Related
- [[auth-and-permissions]]
- [[pagination-and-sorting]]
- [[etags-and-caching]]
""",

    "etags-and-caching.md": """---
title: ETags and Caching
created: 2026-08-14
updated: 2026-08-14
type: concept
tags: [caching, etag, protocol]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# ETags and Caching

To reduce bandwidth, optimize client response times, and avoid redundant fetches over large stashes or pattern catalogs, Ravelry supports HTTP ETags and recommended caching intervals.

## Using ETags

1. When requesting an API endpoint, Ravelry returns an `ETag` response header containing a checksum of the resource state.
2. Store the `ETag` alongside the cached response payload.
3. On subsequent requests, send the `If-None-Match: "<etag>"` header.
4. If the resource has not changed, Ravelry responds with `304 Not Modified` with an empty body, saving round-trip serialization and data transfer.

## Static Reference Data Caching

Certain reference endpoints change infrequently and should be cached locally:
- [[api-reference-data]] (`/fiber_attributes.json`, `/fiber_categories.json`, `/yarn_weights.json`, `/color_families.json`): Cache for up to 24 hours.

---

## Related
- [[http-status-codes-and-errors]]
- [[api-stash]]
- [[api-yarns-and-companies]]
""",

    "input-objects-and-post-data.md": """---
title: Input Objects and POST Data
created: 2026-08-14
updated: 2026-08-14
type: concept
tags: [endpoint, protocol]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Input Objects and POST Data

The Ravelry API supports multiple formats for sending create and update payloads.

## Payload Submission Methods

Methods specifying a parameter named `data` (e.g. `TypeName#POST` objects):

1. **Raw JSON Body (Recommended)**:
   ```http
   POST /people/username/stash/create.json HTTP/1.1
   Content-Type: application/json

   {
     "yarn_id": 1234,
     "colorway_name": "Autumn Hues",
     "skeins": 3
   }
   ```
2. **Form-Encoded with `data` parameter**:
   `POST data={"yarn_id": 1234, "colorway_name": "Autumn Hues"}`
3. **Flat Name/Value Pairs**:
   `POST yarn_id=1234&colorway_name=Autumn+Hues` (Note: nested attributes cannot be represented flat).

---

## Related
- [[auth-and-permissions]]
- [[api-stash]]
- [[api-projects-and-queue]]
- [[stash-model]]
"""
}

for fname, content in concepts.items():
    with open(CONCEPTS_DIR / fname, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# 4. Create Entity Pages
entities = {
    "api-stash.md": """---
title: Stash API Endpoints
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, stash, yarn]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Stash API Endpoints

The Stash API provides methods for searching, querying, creating, modifying, and organizing yarn and fiber stashes.

## Endpoints Summary

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/people/{username}/stash/list.json` | List and search user's stash items | Yes |
| `GET` | `/people/{username}/stash/{id}.json` | Get single stash record details | Yes |
| `POST` | `/people/{username}/stash/create.json` | Create a new stash item | Yes |
| `POST` | `/people/{username}/stash/{id}.json` | Update an existing stash item | Yes |
| `DELETE` | `/people/{username}/stash/{id}.json` | Delete a stash item | Yes |
| `GET` | `/people/{username}/stash/comments.json`| List comments on stash items | Yes |

## Query Parameters for `/people/{username}/stash/list.json`

- `query`: Text search term across stash entries.
- `yarn_id`: Filter stash entries matching a specific [[yarn-model]].
- `fiber_id`: Filter by fiber record.
- `stash_status_id`: Filter by stash status (e.g. in stash, used up, traded).
- `sort`: Sorting field (e.g. `created_`, `yarn_name`, `rating`).
- `page`: Page index (default: `1`).
- `page_size`: Items per page (default: `25`, max: `100`).

## Return Models
- Returns arrays of [[stash-model]] (`Stash (list)` or `Stash (full)`), [[pack-model]] (`Pack`), and [[paginator-model]] (`Paginator`).

---

## Related
- [[stash-model]]
- [[yarn-model]]
- [[pack-model]]
- [[colorway-model]]
- [[input-objects-and-post-data]]
- [[pagination-and-sorting]]
- [[auth-and-permissions]]
""",

    "api-yarns-and-companies.md": """---
title: Yarns and Yarn Companies API
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, yarn, model, search]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Yarns and Yarn Companies API

Provides search, discovery, and detailed lookup for commercial and indie yarns, fiber compositions, and yarn companies.

## Endpoints

### Yarns
- `GET /yarns/search.json`: Full-text & faceted search for yarns with filters for weight, fiber, company, and ratings.
- `GET /yarns/{id}.json`: Detailed record for a single yarn including weight, fiber breakdown, gauge, yardage, and colorways.
- `GET /yarns/{id}/colorways.json`: List of known colorways for a yarn.
- `GET /yarns/{id}/comments.json`: User comments for a yarn.
- `GET /yarns/{id}/photos.json`: Associated user and official photos.

### Yarn Companies
- `GET /yarn_companies/search.json`: Search yarn manufacturers and indie dyers.
- `GET /yarn_companies/{id}.json`: Information on a specific yarn company and its active yarn lines.
- `GET /yarn_companies/{id}/yarns.json`: All yarns produced by a specific company.

---

## Related
- [[yarn-model]]
- [[stash-model]]
- [[colorway-model]]
- [[api-stash]]
- [[api-search]]
- [[api-reference-data]]
""",

    "api-patterns-and-sources.md": """---
title: Patterns and Pattern Sources API
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, pattern, model, search]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Patterns and Pattern Sources API

Endpoints for searching pattern databases, fetching pattern attributes, yarn requirements, needle recommendations, and source publications.

## Endpoints

### Patterns
- `GET /patterns/search.json`: Advanced pattern search with filters (craft, needle size, yardage, category, difficulty).
- `GET /patterns/{id}.json`: Complete pattern metadata, yarn requirements, gauge, needle sizes, and designer info.
- `GET /patterns/{id}/projects.json`: Community projects made from this pattern.

### Pattern Sources & Categories
- `GET /pattern_sources/search.json`: Search books, magazines, and websites.
- `GET /pattern_sources/{id}.json`: Detailed view of a pattern book/source and its pattern list.
- `GET /pattern_categories/list.json`: Hierarchical taxonomy of pattern categories.

---

## Related
- [[pattern-model]]
- [[project-model]]
- [[needle-model]]
- [[api-search]]
- [[api-projects-and-queue]]
""",

    "api-projects-and-queue.md": """---
title: Projects and Queue API
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, project, stash]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Projects and Queue API

Methods for managing knitting/crochet project records, queued projects, and linking stash yarns to projects.

## Endpoints

### Projects
- `GET /people/{username}/projects/list.json`: List user's projects with status, craft, and dates.
- `GET /projects/{username}/{id}.json`: Full project record including used stash packs, needles, and progress notes.
- `POST /projects/{username}/create.json`: Create a new project.
- `POST /projects/{username}/{id}.json`: Update project progress, rating, completion status, or attached stash.
- `DELETE /projects/{username}/{id}.json`: Delete a project record.

### Queued Projects
- `GET /people/{username}/queue/list.json`: User's queued projects and planned yarn pairings.
- `POST /people/{username}/queue/create.json`: Add pattern to queue.
- `POST /people/{username}/queue/reorder.json`: Reorder queue priority.

---

## Related
- [[project-model]]
- [[stash-model]]
- [[pattern-model]]
- [[input-objects-and-post-data]]
- [[api-stash]]
""",

    "api-people-and-current-user.md": """---
title: People and Current User API
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, user, auth]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# People and Current User API

Endpoints for retrieving profile data, verifying authenticated user identity, and social connections.

## Endpoints

- `GET /current_user.json`: Returns the [[user-model]] for the currently authenticated credentials. Key endpoint for initial connection verification in [[StashStats]].
- `GET /people/{username}.json`: Public profile for a user.
- `POST /people/{username}.json`: Update profile info (requires `profile-write` scope).
- `GET /people/{username}/friends/list.json`: List user's friends and activity feeds.
- `GET /people/{username}/favorites/list.json`: List bookmarked/favorited patterns, projects, and yarns.

---

## Related
- [[user-model]]
- [[auth-and-permissions]]
- [[api-app-and-config]]
- [[api-stash]]
""",

    "api-library-and-deliveries.md": """---
title: Library and Deliveries API
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, library, cart]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Library and Deliveries API

Manage digital patterns, purchased ebooks, and library volumes.

## Endpoints

- `GET /people/{username}/library/search.json`: Search and filter patterns/books in user's digital library.
- `GET /deliveries/list.json`: List digital purchases and gifts (requires `deliveries-read` scope).
- `POST /product_attachments/{id}/generate_download_link.json`: Generate secure temporary download link for PDF pattern files (requires `library-pdf` scope).

---

## Related
- [[pattern-model]]
- [[auth-and-permissions]]
- [[cart-and-product-models]]
""",

    "api-forums-and-messages.md": """---
title: Forums and Messages API
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, forum, social]
sources: [raw/articles/ravelry-api-reference.md]
confidence: medium
---

# Forums and Messages API

Endpoints for browsing community boards, reading/writing forum posts, and handling private user messages.

## Endpoints

- `GET /forums/sets.json`: List forum categories and boards.
- `GET /forums/{id}/topics/list.json`: List topics in a forum.
- `GET /topics/{id}.json`: View posts in a thread.
- `POST /forum_posts/create.json`: Post reply (requires `forum-write` scope).
- `GET /messages/list.json`: List private messages (requires `message-read` scope).

---

## Related
- [[forum-models]]
- [[auth-and-permissions]]
- [[user-model]]
""",

    "api-search.md": """---
title: Global Search API
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, search]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Global Search API

Global text search across all entity types in Ravelry.

## Endpoint

`GET /search.json`

### Parameters
- `query`: Text string to search.
- `limit`: Number of results (default `50`, max `500`).
- `types`: Space-delimited list of entity types to include: `User`, `PatternAuthor`, `PatternSource`, `Pattern`, `YarnCompany`, `Yarn`, `Group`, `Event`, `Project`, `Page`, `Topic`, `Shop`.

### Result Object Structure
Each match returns title, `type_name`, thumbnail URLs, and a nested `record` object (`type`, `id`, `permalink`, `uri`).

---

## Related
- [[api-yarns-and-companies]]
- [[api-patterns-and-sources]]
- [[api-stash]]
""",

    "api-app-and-config.md": """---
title: App Configuration and Storage API
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, app, config]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# App Configuration and Storage API

Ravelry provides dedicated cloud key-value storage for third-party applications to sync user preferences, settings, and state across devices.

## Endpoints

- `GET /app/data/get.json?keys=key1+key2`: Retrieve stored user key/value pairs.
- `POST /app/data/set.json`: Store user-specific application data.
- `POST /app/data/delete.json`: Delete key/value entries.
- `POST /app/config/set.json`: Configure app-level settings (e.g. `profile_badge=1`).

---

## Related
- [[auth-and-permissions]]
- [[api-people-and-current-user]]
- [[user-model]]
""",

    "api-reference-data.md": """---
title: Reference Data API (Colors, Fibers, Weights, Needles)
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, model, yarn]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Reference Data API (Colors, Fibers, Weights, Needles)

Static and semi-static taxonomy endpoints used to normalize stash and pattern data.

## Endpoints

- `GET /color_families.json`: Master list of color families (e.g. Red, Blue, Neutral, Multi).
- `GET /fiber_categories.json`: Categories of fiber (e.g. Animal, Plant, Synthetic).
- `GET /fiber_attributes.json`: Specific fiber types (e.g. Merino, Silk, Cashmere, Acrylic).
- `GET /yarn_weights.json`: Standard yarn weight classifications (Lace, Fingering, Sport, DK, Worsted, Bulky, Super Bulky).
- `GET /needles/sizes.json`: Knitting needle and crochet hook metric and US sizes.

> [!TIP]
> These endpoints do not require authentication and change very infrequently. Cache responses locally for up to 24 hours as described in [[etags-and-caching]].

---

## Related
- [[etags-and-caching]]
- [[yarn-model]]
- [[needle-model]]
- [[colorway-model]]
""",

    "api-carts-and-stores.md": """---
title: Carts and Stores API
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, cart, store]
sources: [raw/articles/ravelry-api-reference.md]
confidence: medium
---

# Carts and Stores API

Endpoints for integrating third-party e-commerce stores with Ravelry's pattern purchasing and library delivery infrastructure.

## Endpoints

- `POST /carts/create.json`: Create a cart associated with a store ID.
- `POST /carts/{id}/add.json`: Add digital pattern products via item code (SKU).
- `POST /carts/{id}/external_checkout.json`: Notify Ravelry of external payment to trigger automatic library delivery to the buyer.

---

## Related
- [[cart-and-product-models]]
- [[auth-and-permissions]]
- [[api-library-and-deliveries]]
""",

    "stash-model.md": """---
title: Stash Data Model
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [model, stash, yarn]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Stash Data Model

The `Stash` model represents a user's yarn or fiber holding in Ravelry.

## Core Schema Fields

| Field Name | Type | Description |
|---|---|---|
| `id` | Integer | Unique identifier for the stash entry |
| `name` | String | User's custom nickname for this stash item |
| `yarn_id` | Integer | ID of linked [[yarn-model]] |
| `yarn` | Object | Full nested [[yarn-model]] record |
| `colorway_name` | String | Colorway name or identifier |
| `dye_lot` | String | Dye lot code |
| `skeins` | Float | Quantity of full or partial skeins |
| `grams` | Float | Total weight in grams |
| `yards` | Float | Total length in yards |
| `meters` | Float | Total length in meters |
| `location` | String | Storage bin, room, or shelf note |
| `packs` | Array | Array of individual [[pack-model]] instances |
| `stash_status` | Object | Status (e.g. `in_stash`, `used_up`, `traded`) |
| `has_photos` | Boolean | True if user uploaded photos |
| `photos` | Array | Array of photo attachments |
| `notes` | String | User notes in markdown/text |
| `created_at` | String | ISO Timestamp |
| `updated_at` | String | ISO Timestamp |

## Related Models
- `UnifiedStash`: Combines yarn stash and fiber stash records into a single uniform representation.
- `FiberStash`: Stash record specifically for unspun spinning fiber.
- `QueuedStash`: Stash item allocated or reserved for a specific [[project-model]].

---

## Related
- [[api-stash]]
- [[yarn-model]]
- [[pack-model]]
- [[colorway-model]]
- [[project-model]]
""",

    "yarn-model.md": """---
title: Yarn Data Model
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [model, yarn]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Yarn Data Model

Represents a commercial or hand-dyed yarn base in Ravelry's database.

## Core Schema Fields

| Field Name | Type | Description |
|---|---|---|
| `id` | Integer | Primary key of yarn |
| `name` | String | Yarn name (e.g. "Sock", "Tosh Merino Light") |
| `yarn_company_name` | String | Brand / Dyer name |
| `yarn_company_id` | Integer | ID of yarn company |
| `yarn_weight` | Object | Weight classification object (name, ply, wpi, min_gauge, max_gauge) |
| `grams` | Integer | Unit skein weight in grams |
| `yardage` | Integer | Unit skein yardage |
| `meterage` | Integer | Unit skein meterage |
| `gauge_divisor` | Integer | Stitch gauge measurement window (usually 4 inches / 10 cm) |
| `min_gauge` / `max_gauge` | Float | Recommended gauge range |
| `yarn_fibers` | Array | Composition list of fiber types and percentages |
| `texture` | String | Description of plies and spin (e.g. "plied", "singles", "boucle") |
| `rating_average` | Float | Community rating (1.0 to 5.0) |
| `rating_count` | Integer | Total community reviews |
| `stashes_count` | Integer | Number of users with this yarn in their stash |
| `projects_count` | Integer | Number of projects made with this yarn |

---

## Related
- [[stash-model]]
- [[api-yarns-and-companies]]
- [[colorway-model]]
- [[api-reference-data]]
""",

    "pattern-model.md": """---
title: Pattern Data Model
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [model, pattern, craft]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Pattern Data Model

Represents a knitting, crochet, weaving, or machine-knitting design pattern.

## Core Schema Fields

| Field Name | Type | Description |
|---|---|---|
| `id` | Integer | Pattern unique ID |
| `name` | String | Pattern title |
| `pattern_author` | Object | Designer details (id, name, permalink) |
| `craft` | Object | Craft classification (Knitting, Crochet, Weaving, Machine Knitting, Loom Knitting) |
| `pattern_categories` | Array | Hierarchical categories (e.g. Clothing -> Sweater -> Pullover) |
| `yardage` / `yardage_max` | Integer | Required yardage range |
| `yarn_weight` | Object | Target yarn weight |
| `gauge` | Float | Stitches per gauge divisor |
| `gauge_divisor` | Integer | Measurement span (inches) |
| `gauge_description`| String | Gauge details and stitch pattern |
| `needle_sizes` | Array | Recommended [[needle-model]] sizes |
| `packs` | Array | Suggested yarn packs & quantities |
| `rating_average` | Float | Community rating |
| `difficulty_average`| Float | Difficulty score (1.0 = Piece of Cake, 10.0 = Hard) |
| `downloadable` | Boolean | True if digital PDF available via Ravelry |
| `free` | Boolean | True if free pattern |

---

## Related
- [[api-patterns-and-sources]]
- [[project-model]]
- [[yarn-model]]
- [[needle-model]]
""",

    "project-model.md": """---
title: Project Data Model
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [model, project, stash]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Project Data Model

Represents an individual user's crafted project instance.

## Core Schema Fields

| Field Name | Type | Description |
|---|---|---|
| `id` | Integer | Project ID |
| `name` | String | Project title given by user |
| `pattern_id` | Integer | Linked [[pattern-model]] ID |
| `craft_id` | Integer | Craft type ID (Knitting, Crochet, etc.) |
| `status_name` | String | Status (`In progress`, `Finished`, `Hibernating`, `Frogged`) |
| `progress` | Integer | Percent completed (0 to 100) |
| `rating` | Integer | User rating of pattern experience |
| `started` | String | Date started (YYYY-MM-DD) |
| `completed` | String | Date completed (YYYY-MM-DD) |
| `packs` | Array | Array of [[pack-model]] allocations from stash |
| `needle_sizes` | Array | Needles/hooks used for this project |
| `size_name` | String | Pattern size knitted/crocheted |
| `made_for` | String | Recipient of project |
| `notes` | String | Project notes and modifications |

---

## Related
- [[api-projects-and-queue]]
- [[stash-model]]
- [[pattern-model]]
- [[needle-model]]
""",

    "user-model.md": """---
title: User Data Model
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [model, user, auth]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# User Data Model

Represents a Ravelry user account and identity.

## Core Schema Fields

| Field Name | Type | Description |
|---|---|---|
| `id` | Integer | Unique user ID |
| `username` | String | Ravelry login username / permalink |
| `photo_url` | String | Avatar image URL |
| `large_photo_url` | String | High-res avatar image URL |
| `location` | String | User location text |
| `about_me` | String | User bio |
| `fav_curator` | Boolean | True if user is a featured favorites curator |
| `designer` | Boolean | True if user has published designs |
| `pattern_author` | Object | Designer profile record if applicable |

---

## Related
- [[api-people-and-current-user]]
- [[auth-and-permissions]]
- [[stash-model]]
- [[project-model]]
""",

    "needle-model.md": """---
title: Needle and Tool Data Model
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [model, needle, craft]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Needle and Tool Data Model

Represents knitting needles, crochet hooks, and tools in a user's inventory or pattern specifications.

## Core Schema Fields

| Field Name | Type | Description |
|---|---|---|
| `id` | Integer | Unique needle size ID |
| `metric` | Float | Size in millimeters (e.g. 4.0) |
| `us` | String | US size designation (e.g. "6") |
| `uk` | String | UK size designation (e.g. "8") |
| `crochet` | String | Crochet hook letter designation (e.g. "G-6") |
| `length` | Float | Needle / cord length |
| `needle_type` | Object | Type (`circular`, `straight`, `dpn`, `interchangeable`) |

---

## Related
- [[pattern-model]]
- [[project-model]]
- [[api-reference-data]]
""",

    "pack-model.md": """---
title: Pack and Colorway Allocation Model
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [model, stash, yarn]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Pack and Colorway Allocation Model

The `Pack` object represents a specific batch or grouping of skeins within a stash or project entry.

## Core Schema Fields

| Field Name | Type | Description |
|---|---|---|
| `id` | Integer | Pack ID |
| `stash_id` | Integer | Parent [[stash-model]] ID |
| `yarn_id` | Integer | Associated [[yarn-model]] ID |
| `colorway_name` | String | Name of colorway |
| `color_family_id` | Integer | Associated color family |
| `dye_lot` | String | Dye lot identifier |
| `skeins` | Float | Number of skeins in this pack |
| `grams` | Float | Weight in grams |
| `yards` | Float | Yardage |
| `meters` | Float | Meterage |
| `shop_name` | String | Store where purchased |
| `total_paid` | Float | Purchase cost |
| `currency` | String | ISO Currency code (USD, EUR, GBP, etc.) |

---

## Related
- [[stash-model]]
- [[colorway-model]]
- [[yarn-model]]
""",

    "colorway-model.md": """---
title: Colorway and Color Family Model
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [model, yarn, stash]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Colorway and Color Family Model

Colorways represent specific color names and dye formulas for yarns and fiber.

## Color Families
Standardized Ravelry color categories used for faceted search and visualization:
- Black, Grey, White, Natural/Undyed
- Red, Pink, Orange, Yellow, Green, Blue, Purple
- Brown, Multi-color, Variegated, Self-striping

---

## Related
- [[pack-model]]
- [[stash-model]]
- [[yarn-model]]
- [[api-reference-data]]
""",

    "paginator-model.md": """---
title: Paginator Model
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [model, pagination, protocol]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Paginator Model

Standard response envelope accompanying all paginated API queries.

## Schema Fields

| Field Name | Type | Description |
|---|---|---|
| `page` | Integer | Current active page (1-indexed) |
| `page_count` | Integer | Total number of pages |
| `page_size` | Integer | Number of items per page |
| `results` | Integer | Total count of matching items across all pages |
| `last_page` | Boolean | True if current page is the final page |

---

## Related
- [[pagination-and-sorting]]
- [[api-stash]]
- [[api-patterns-and-sources]]
""",

    "cart-and-product-models.md": """---
title: Cart, Product, and Invoice Models
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [model, cart, store]
sources: [raw/articles/ravelry-api-reference.md]
confidence: medium
---

# Cart, Product, and Invoice Models

Models representing commercial digital pattern transactions and library attachments.

## Core Models
- `Cart`: Active shopping cart with store association and items.
- `CartItem`: Individual product line item in cart.
- `Invoice`: Paid transaction receipt delivering pattern attachments to user library.
- `ProductAttachment`: Digital PDF download link asset.

---

## Related
- [[api-carts-and-stores]]
- [[api-library-and-deliveries]]
- [[auth-and-permissions]]
""",

    "forum-models.md": """---
title: Forum, Topic, and Message Models
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [model, forum, social]
sources: [raw/articles/ravelry-api-reference.md]
confidence: medium
---

# Forum, Topic, and Message Models

Models representing community board discussions, replies, and private messaging.

## Core Models
- `Forum`: Board category or group discussion section.
- `Topic`: Threaded conversation topic with reply counts.
- `ForumPost`: Individual message within a topic.
- `Message`: Direct user-to-user private message.

---

## Related
- [[api-forums-and-messages]]
- [[user-model]]
- [[auth-and-permissions]]
"""
}

for fname, content in entities.items():
    with open(ENTITIES_DIR / fname, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# 5. Build index.md
index_content = """# Wiki Index

> Content catalog for Ravelry API Documentation & StashStats Architecture.
> Read this first to find relevant pages for any query.
> Last updated: 2026-08-14 | Total pages: 23

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
"""

with open(WIKI_DIR / "index.md", "w", encoding="utf-8") as f:
    f.write(index_content)

# 6. Build log.md
log_content = """# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, archive, delete
> When this file exceeds 500 entries, rotate: rename to log-YYYY.md, start fresh.

## [2026-08-14] create | Wiki initialized
- Domain: Ravelry API Documentation & StashStats Architecture
- Structure created with SCHEMA.md, index.md, log.md

## [2026-08-14] ingest | Ravelry API Complete Documentation
- Ingested source `StashDraft.md` to `raw/articles/ravelry-api-reference.md`
- Created 5 Concept pages:
  - `concepts/auth-and-permissions.md`
  - `concepts/pagination-and-sorting.md`
  - `concepts/http-status-codes-and-errors.md`
  - `concepts/etags-and-caching.md`
  - `concepts/input-objects-and-post-data.md`
- Created 11 API Endpoint Entity pages:
  - `entities/api-stash.md`
  - `entities/api-yarns-and-companies.md`
  - `entities/api-patterns-and-sources.md`
  - `entities/api-projects-and-queue.md`
  - `entities/api-people-and-current-user.md`
  - `entities/api-library-and-deliveries.md`
  - `entities/api-forums-and-messages.md`
  - `entities/api-search.md`
  - `entities/api-app-and-config.md`
  - `entities/api-reference-data.md`
  - `entities/api-carts-and-stores.md`
- Created 11 Data Model Entity pages:
  - `entities/stash-model.md`
  - `entities/yarn-model.md`
  - `entities/pattern-model.md`
  - `entities/project-model.md`
  - `entities/user-model.md`
  - `entities/needle-model.md`
  - `entities/pack-model.md`
  - `entities/colorway-model.md`
  - `entities/paginator-model.md`
  - `entities/cart-and-product-models.md`
  - `entities/forum-models.md`
- Verified bidirectional wikilinks, index completeness, and frontmatter taxonomy compliance.
"""

with open(WIKI_DIR / "log.md", "w", encoding="utf-8") as f:
    f.write(log_content)

print("Wiki updated and compiled successfully.")
