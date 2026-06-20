---
aliases:
  - "Basic HTTP Auth"
tags:
  - ravelry
  - documentation
---

# Ravelry Basic HTTP Auth

**Basic HTTP Authentication serves as the straightforward, developer-centric access model** within the Ravelry API ecosystem, intentionally designed for data scientists, researchers, and developers building personal automation tools or server-side scripts. While public-facing, multi-user applications require dynamic OAuth protocols to protect user credentials, Basic Auth is structurally utilized to avoid complex permission scopes for internal workflows and data harvesting.

Within the Ravelry API, Basic Authentication is divided into two distinct access tiers, each requiring specific credentials provisioned from the Ravelry Pro portal:

### 1. Read-Only Access
This modality is designed for applications or scripts that only need to harvest data from Ravelry's public global databases, such as searching for yarn weights or querying pattern categories. 
*   **Credentials:** Developers authenticate by passing their **Access Key** as the username and their **Secret Key** as the password.
*   **Limitations:** When utilizing read-only credentials, developers are restricted exclusively to API methods that are not marked as "authenticated" in the API documentation.

### 2. Personal Account Access
If a developer is building a tool exclusively for their own use, they can bypass OAuth permission scopes by using Personal Account Access. 
*   **Credentials:** Under this tier, the developer authenticates using their **Access Key** as the username, but substitutes a dedicated **Personal Key** (instead of the secret key) as the password.
*   **Capabilities:** This method automatically grants the script full, unrestricted access to the developer's personal Ravelry account and "Notebook," making it ideal for personal projects managing private stash or queue data.

### Technical Implementation and Security Constraints
Regardless of the access tier used, Ravelry enforces strict security protocols for Basic Authentication:
*   **SSL Requirement:** All requests must be transmitted over SSL/HTTPS. If a developer attempts to authenticate over standard HTTP, the API will immediately reject the request with a **403 Forbidden** error.
*   **Header Encoding:** From an engineering perspective, the client application must concatenate the username and password with a separating colon (`username:password`), convert this combined string into a Base64-encoded representation, and append it to the HTTP `Authorization` request header.

### Integration within the Developer Ecosystem
Because of its simplicity, Basic HTTP Auth is the foundational engine for several major segments of the Ravelry developer ecosystem:

*   **Data Science Pipelines (R and `ravelRy`):** Data analysts relying on the `ravelRy` R package use Read-Only Basic Authentication to scrape pattern and yarn data for statistical modeling. The package is engineered to automatically look for `RAVELRY_USERNAME` and `RAVELRY_PASSWORD` environment variables in a user's local `.Renviron` file, or developers can set them directly in the active R console using the `ravelry_auth()` helper function. 
*   **Python Automation (`knotion`):** Developers building custom synchronization scripts, such as the `knotion` project which pushes a crafter's Ravelry stash and queue data into Notion databases, rely specifically on the "HTTP Basic Auth: personal account access" tier. This safely exposes the user's private inventory without requiring OAuth setups.
*   **PHP Libraries:** Backend PHP frameworks, such as the `theloopyewe-ravelry-api.php` library, actively implement Basic Authentication endpoints, allowing developers to configure personal use integrations by passing their access and personal keys.
*   **Artificial Intelligence and MCP Servers:** Basic Auth is utilized to bridge Ravelry with Large Language Models. The `MCP_ravelry` server uses the Model Context Protocol to allow AI assistants like Claude to autonomously search for knitting patterns. Developers embed their Ravelry username and password directly into local `.env.development` or `.env.production` files, which the server uses to securely authenticate API requests using libraries like `axios`.

### Common Troubleshooting and Edge Cases
A well-documented quirk within Ravelry's Basic Authentication gateway relates to how the server handles malformed local credential files. 

Data scientists frequently store their Basic Auth credentials in local text files (such as `user_rav.txt` when using R's `httr` library). If a developer makes a typo in the column headers or slightly misaligns the formatting within these credential files, Ravelry's server parsing engine crashes upon receiving the malformed authentication string. Instead of returning a standard **401 Unauthorized** error, the API generates a cryptic **500 Internal Server Error**, which frequently confuses developers attempting to debug their initial connection pipelines.
