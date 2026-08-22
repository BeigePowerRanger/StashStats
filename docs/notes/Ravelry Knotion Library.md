---
aliases:
  - "Knotion library"
tags:
  - ravelry
  - documentation
---

# Ravelry Knotion Library

**Knotion** (a blend of "Knitting" and "Notion") is a specialized open-source project consisting primarily of Jupyter Notebooks and Python functions designed to bridge the Ravelry and Notion APIs, effectively allowing the two platforms to "talk to each other". 

Created by developer `mjms`, Knotion occupies a highly specific niche within the broader Ravelry developer ecosystem: **personal workflow automation and inventory synchronization**. Rather than building a public mobile app or a broad data science pipeline to harvest global catalogs, Knotion is engineered to seamlessly push a crafter's private Ravelry data directly into their structural Notion databases.

Here is a detailed overview of Knotion's architecture and its role within the Ravelry API ecosystem:

### 1. Focus on the "Personal Notebook" (Scope and Exclusions)
Within the Ravelry API ecosystem, developer tools generally fall into two categories: those that harvest global catalogs, and those that manage personal user content. Knotion falls strictly into the latter. 
*   **Out-of-Scope Endpoints:** In architectural reviews mapping the Python ecosystem, Knotion explicitly ignores Ravelry's global discovery features. Endpoints such as `/patterns/search`, `yarn_weights`, and `yarn_attributes` are considered entirely "Out-of-Scope" for the project. 
*   **Custom User Implementation:** Instead, Knotion focuses its development strictly on validating the `current_user` and building custom implementations for a user's private `stash/notebook` and `queue/notebook` endpoints.

### 2. Defensive Data Parsing (`parse_stash_pack()`)
A major challenge when interacting with the Ravelry API is navigating its deeply nested JSON payloads, particularly when dealing with personal inventory. To handle this, Knotion employs defensive parsing routines that extract complex data into clean, relational database columns. 
*   **Targeted Extraction:** The library features a specific function named **`parse_stash_pack()`**. This routine is explicitly engineered to drill into the complex `packs` arrays within a user's stash payload, extracting vital granular details such as yarn weights, community ratings, and fiber components, and flattening them into a structural format. 
*   **Notion Integration and Roadmap:** On the destination side, the script includes Notion-specific utility functions like `check_notion()` and `add_new_property()` to programmatically build the target database. The project's ongoing development roadmap includes expanding these capabilities to pull broader yarn information directly from the Ravelry database and format it into the strict payload structures required by the Notion API.

### 3. Ecosystem Authentication Profile
Because Knotion is designed as a personal, server-side synchronization script rather than a distributed public application, it avoids the complexities of dynamic OAuth 2.0 flows. 
*   **Personal Account Access:** The library explicitly requires the API tier **"HTTP Basic Auth: personal account access"**. By utilizing the developer's Access Key as the username and a dedicated Personal Key as the password, Knotion is granted full, secure read access to the user's private inventory without needing to configure complex permission scopes or callback URLs. 
*   **Accessibility:** Additionally, the tool is designed to be highly accessible for everyday crafters, engineered to function fully on a free-tier Notion account.
