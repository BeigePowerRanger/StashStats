---
aliases:
  - "Endpoint Design"
tags:
  - ravelry
  - documentation
---

# Ravelry Endpoint Design

**Endpoint design within the Ravelry API ecosystem** is fundamentally structured around a RESTful architecture that categorizes data into strict "Domain Entities." This design balances the platform's vast global crafting databases with highly private user inventories, dictating how developers build wrappers, perform data extraction, and handle security.

Here is a detailed, comprehensive overview of how Ravelry's endpoints are designed and how they influence the broader developer ecosystem:

### 1. Domain Entity Routing and Categorization
Ravelry’s API paths are logically separated into specific domains, which dictate whether a developer is interacting with the master database or a specific crafter's "Notebook".
*   **Global Taxonomies:** Endpoints that serve foundational reference data or global catalogs are routed directly at the root level. Examples include `/color_families.json`, `/yarn_weights.json`, `/fiber_categories.json`, and `/patterns/search.json`. These endpoints are heavily utilized by data science packages (like R's `ravelRy`) and global backend SDKs (like Go's `go-ravelry`) to map master metrics.
*   **Personal User Inventories:** Endpoints dealing with a user's private data require strict user context in the URL path. These are designed using the `/people/{username}/...` structure. For example, accessing a user's yarn inventory or planned projects requires calling `/people/{username}/stash/list.json` or `/people/{username}/queue/list.json`. Highly specialized ecosystem tools, like the Python library `knotion`, restrict their entire architecture exclusively to these personal endpoints.

### 2. Nested JSON Payloads and Defensive Parsing
A defining characteristic of Ravelry's endpoint design is that responses return **highly hierarchical, deeply nested JSON payloads** rather than flat relational tables. 
*   **The "Pippi Pullover" Payload:** When querying a specific item, such as through the `/patterns.json?ids=pippi-pullover` endpoint, the returned JSON object contains complex nested arrays detailing the designer's attributes, required material `packs`, gauge metrics, and recommended needle sizes. 
*   **Ecosystem Impact:** Because the API returns such dense data, developers cannot simply plug the API output directly into a database. The ecosystem relies heavily on developers engineering defensive parsing routines (like `knotion`'s `parse_stash_pack()` function) to drill into these payloads and flatten the arrays into usable dictionaries or data frames. 

### 3. Standardized Pagination Metadata
To manage massive datasets, Ravelry's list-based and search-based endpoints utilize a highly standardized pagination design. 
*   Endpoints accept `page` and `page_size` query parameters.
*   Instead of just returning an array of items, **these endpoints consistently wrap the results alongside a dedicated `Paginator` object**. This object contains predictable metadata properties: `page_count`, `page`, `page_size`, `results`, and `last_page`. This uniform design allows developers across Python, R, Kotlin, and PHP to write reusable looping scripts that automatically traverse hundreds of pages of search results without needing to write custom pagination logic for every single endpoint.

### 4. Input Flexibility for Data Mutation (POST/PUT)
For endpoints designed to create or modify data (such as creating a project or updating a stash entry), Ravelry's design is highly flexible regarding input formats.
*   The endpoints accept either **standard URL-encoded name/value pairs** or **raw JSON payloads**. 
*   However, the design enforces a strict constraint: if a developer needs to submit nested data structures (such as adding specific yarn "packs" to a new project), they must use the JSON format and POST it via a parameter explicitly named `data`, or submit it as the raw POST body.

### 5. Strict Coupling with Authorization Scopes
Endpoint access is structurally intertwined with Ravelry's granular OAuth 2.0 permission scopes. The API is designed so that specific endpoints are hard-locked behind designated privileges:
*   **Social Interactions:** Endpoints like `/messages/create.json` or `/forum_posts/{forum_post_id}.json` require the explicit `message-write` or `forum-write` scopes. 
*   **Commercial Security:** Endpoints dealing with copyrighted digital downloads—specifically `/product_attachments/{id}/generate_download_link.json`—require the highly restricted `library-pdf` or `patternstore-pdf` scopes. Because this endpoint generates links to commercial files, Ravelry's design dictates that OAuth tokens requesting this scope expire much faster than standard tokens and are subject to rigid rate limits (currently capped at 100 requests per day).

### 6. Client-Side Object-Oriented Translation
Because REST APIs rely on explicit URL paths that can sometimes be cumbersome to call repeatedly, a common design pattern within the Ravelry developer ecosystem is to abstract these endpoints into **object-oriented class methods**. 
Following patterns established by community packages across various languages, developers map raw REST endpoints into intuitive, camelCase functions. For example, instead of manually writing a POST request to `/messages/mark_read`, wrapper libraries translate this endpoint design into a client-side method like `rav.messages.markRead()`, streamlining the developer experience and ensuring strict argument ordering.
