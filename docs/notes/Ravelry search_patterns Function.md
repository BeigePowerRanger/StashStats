---
aliases:
  - "search_patterns()"
tags:
  - ravelry
  - documentation
---

# Ravelry search_patterns Function

**`search_patterns()`** serves as the primary programmatic discovery engine for navigating Ravelry's massive design database. Under the hood, this function acts as a wrapper for the Ravelry API’s highly specialized `/patterns/search.json` endpoint. Unlike the API's global `/search.json` method—which is a simple, text-only search across all entities—the pattern search endpoint is explicitly designed to handle the platform's granular crafting taxonomies and advanced filtering capabilities. 

Here is a detailed overview of how the sources describe `search_patterns()` and its role within the broader API ecosystem:

### 1. Advanced Filtering and Parameters
The true power of `search_patterns()` lies in its flexibility. Rather than being restricted to basic keyword queries, the endpoint allows developers to pass virtually any advanced filter parameter that is available on the main Ravelry website's search interface.
*   **Base Parameters:** At its core, the function accepts a `query` (a search string like "hat" or "cowl"), a `page` number, and a `page_size` (which defaults to 100 in the API).
*   **Dynamic Taxonomies:** Developers can dynamically filter the database by appending specific taxonomy constraints. In the R package `ravelRy`, this is handled via the ellipses (`...`) argument, allowing analysts to pass parameters like `craft`, `availability`, `fit`, `weight`, and `photo`. For instance, a query can be strictly narrowed down by passing `availability = 'free'` and `fit = 'baby'`. 
*   **Direct ID Targeting:** The API endpoint also supports filtering by an exact list of designs. By passing a pipe-delimited (`|`) list of integer IDs to the `pattern_id` parameter, developers can retrieve basic details for a specific, pre-defined set of patterns. 

### 2. Injecting Personal User Context
Within the Ravelry ecosystem, `search_patterns()` bridges the gap between global discovery and the user's personal "Notebook". 
*   By passing the **`personal_attributes=1`** boolean parameter to the API request, the resulting JSON payload injects a special `personal_attributes` hash into each returned pattern object. 
*   This hash reveals the item's relational status to the currently authenticated user, indicating whether they have already favorited the pattern, added it to their queue, or attached a bookmark ID to it.

### 3. The "Two-Step" Data Extraction Pipeline
Across data science workflows, `search_patterns()` is structurally designed as "Step 1" in a two-step extraction pipeline. Because the complete metadata payload for a single pattern is incredibly dense—containing arrays of exact yardages, needle sizes, and fiber compositions—it is computationally inefficient to download full payloads in bulk.
*   **Step 1 (Discovery):** The developer uses `search_patterns()` to execute their targeted query. The endpoint returns a lightweight list of patterns, parsed in the `ravelRy` package as a flattened "tibble". This tibble contains only high-level identifiers, boolean flags (like `free`), and basic designer information. 
*   **Step 2 (Deep Extraction):** The analyst isolates the resulting pattern IDs (e.g., `search_results$id`) and passes that specific vector into the `get_patterns()` function (which maps to the `/patterns.json` endpoint). This retrieves the heavy, deeply nested technical specifications only for the exact subset of patterns needed for their analysis.

### 4. Implementation Across the Developer Ecosystem
Because pattern discovery is a core system functionality, the `/patterns/search` endpoint is widely implemented across the third-party developer landscape:
*   **Data Science (R):** The `ravelRy` package fully supports this endpoint, automatically flattening the deeply nested JSON pagination objects into user-friendly tibbles ready for exploration.
*   **Backend Services (Go):** The unofficial `go-ravelry` SDK actively implements this endpoint to power high-performance, compiled backend services.
*   **AI Integration (MCP):** The `MCP_ravelry` server exposes this endpoint directly to Large Language Models (like Claude) via the **`search-patterns`** tool. It wraps parameters like `query`, `craft`, and `availability` so that an AI assistant can autonomously process a natural language prompt (e.g., "Find me some free crochet hat patterns on Ravelry") and execute the corresponding API search using the user's credentials.
*   **Targeted Exclusions (Python):** Conversely, tools explicitly built for personal user-inventory management—like the Python script library `knotion`, which pushes user stash data into Notion databases—consider the global pattern search endpoint to be "Out-of-Scope," focusing strictly on personal user records instead.
