---
aliases:
  - "get_yarns()"
tags:
  - ravelry
  - documentation
---

# Ravelry get_yarns Function

**`get_yarns()`** is a highly specialized data extraction function within the **`ravelRy`** package for the R programming language. Within the larger Ravelry API ecosystem, it is designed for data scientists and researchers who need to pull exhaustive technical and material specifications for specific yarns and format them for statistical analysis. 

Here is a detailed overview of how the sources describe `get_yarns()` and its structural role within the developer ecosystem:

### 1. Function Mechanics and Targeted Retrieval
Unlike discovery functions in the API ecosystem that accept descriptive natural language queries (like `search_yarn()`), `get_yarns()` relies exclusively on exact database identifiers. 
*   **The `ids` Argument:** The function requires the `ids` argument, which accepts a vector of one or more specific `yarn_id` integers. 
*   **Example Usage:** An analyst would execute a command such as `get_yarns(ids = c(66124, 54110))` to directly query Ravelry's master database for those exact physical materials.

### 2. Parsing Deep JSON into Analysis-Ready "Tibbles"
A fundamental challenge of the Ravelry API is its highly nested, complex JSON payloads. A single yarn entry contains deep data structures for fiber composition, weight standards, and manufacturing details.
*   **Automatic Flattening:** Built using modern R data manipulation packages like `dplyr`, `tidyr`, `purrr`, and `jsonlite`, the `ravelRy` package automatically parses and flattens these complex API responses.
*   **Rich Metadata Output:** When `get_yarns()` successfully executes, it returns a **tibble** (a modern R data frame). This tibble cleanly organizes the granular material and community details needed for fiber analysis, exposing variables such as the yarn's manufacturing `company`, physical `grams`, standardized `gauge`, textile `texture`, recommended `needle_sizes`, and community `ratings`.

### 3. The "Two-Step" Material Data Pipeline
Within the overall ecosystem of `ravelRy`, `get_yarns()` acts as the heavy-lifting second half of a modular data extraction pipeline. Because downloading deeply nested metadata payloads in bulk for thousands of yarns would be computationally inefficient and could strain API rate limits, data scientists utilize a two-step workflow:
1.  **Broad Discovery (`search_yarn`):** Analysts first use the `search_yarn()` function, passing advanced filters (such as `query = 'cascade'` and `weight = 'sport'`) to locate a broad category of materials. This returns a lightweight tibble containing basic details and a column of specific yarn IDs.
2.  **Deep Extraction (`get_yarns`):** Analysts then isolate those specific IDs and feed them directly into **`get_yarns()`**. This ensures the script only downloads the heavy technical specifications for the exact subset of yarns required for their statistical model.

### 4. Integration with Ecosystem Authentication
Because `get_yarns()` accesses Ravelry's global yarn databases, it relies on the API's **Basic HTTP Authentication (Read-Only access)**. 
*   Before calling `get_yarns()`, an analyst must securely establish their connection to the API by provisioning a free Ravelry developer Access Key and Secret Key. 
*   Within the `ravelRy` package, these credentials must reside in the local system's hidden `.Renviron` variables (`RAVELRY_USERNAME` and `RAVELRY_PASSWORD`), or they can be dynamically loaded into the active R console using the `ravelry_auth()` helper function. Once authenticated, `get_yarns()` is authorized to autonomously ping the API and retrieve the fiber data.
