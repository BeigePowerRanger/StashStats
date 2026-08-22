---
aliases:
  - "Security & Setup"
tags:
  - ravelry
  - documentation
---

# Ravelry Security and Setup

**Security and Setup form the foundational gateway to the Ravelry API ecosystem**, establishing strict boundaries that protect Ravelry’s massive crafting database and the private data of its millions of users while enabling third-party developer innovation. Because the platform manages sensitive user information—ranging from private messages to copyrighted digital pattern libraries—Ravelry enforces a highly structured provisioning process, specific authentication modalities, and stringent operational guidelines.

Here is a detailed overview of how Security and Setup function within the overall Ravelry API ecosystem:

### 1. Developer Provisioning and Credential Generation
Before an application or script can interact with the API, developers must formally establish their identity with the platform.
*   **The Ravelry Pro Portal:** Every integration begins by visiting the Ravelry Pro portal (`https://www.ravelry.com/pro/developer`), where a developer can create a free account and register their application. 
*   **Generating Keys:** Depending on the type of application being built, developers use this portal to provision specific security keys. For simple data extraction scripts, they generate an **Access Key**, a **Secret Key**, and a **Personal Key**. For distributed web or mobile applications, they must register an OAuth application to receive a `client_id` and a `client_secret`.

### 2. Mandatory Authentication Modalities
Ravelry employs two primary authentication architectures. **A universal security constraint across both models is that all API requests must be transmitted over SSL/HTTPS**; attempting to authenticate over a standard HTTP connection will result in an immediate HTTP 403 Forbidden error.

**Basic HTTP Authentication**
This model is intentionally designed for server-side scripts, data science pipelines, and personal automation tools.
*   **Read-Only Access:** Developers authenticate by passing their Access Key as the username and their Secret Key as the password. This allows scripts to harvest data from unauthenticated endpoints in Ravelry's public global databases (like pattern or yarn catalogs). 
*   **Personal Account Access:** Developers authenticate by passing their Access Key as the username and substituting their **Personal Key** as the password. This grants a personal script full, unrestricted access to the developer's own Ravelry account and "Notebook" without needing to request specialized OAuth permissions. 
*   **Cryptographic Encoding:** Structurally, the client application must concatenate the username and password with a separating colon (`username:password`), convert this string into a Base64-encoded format, and append it to the HTTP `Authorization` request header.

**OAuth 1.0a and OAuth 2.0**
For public-facing applications (such as third-party Android apps or web dashboards) where end-users must log into their own accounts, dynamic OAuth flows are strictly required to prevent credential exposure.
*   **Strict Security Validators:** Ravelry enforces a highly specific, often undocumented security constraint within its OAuth 2.0 gateway: **the authorization `state` parameter must be a secure, random string strictly greater than eight characters in length**. Submitting a shorter string triggers an immediate authorization failure. Furthermore, Ravelry explicitly prohibits "Out-of-Band" (OOB) authorization, requiring apps to use strict callback URLs or app schemes to catch token redirects.
*   **Token Lifecycle:** OAuth 2.0 access tokens **expire in 24 hours**. Applications must explicitly request the `offline` scope to receive a refresh token, allowing the client library to silently re-authenticate users before the token expires or gracefully handle HTTP 401 Unauthorized responses. Legacy OAuth 1.0a tokens are long-lived but can still expire after inactivity or manual revocation.

### 3. Granular Authorization Scopes (Permissions)
When utilizing OAuth, security is further tightened through granular permission scopes. Applications must explicitly request the exact privileges they need by separating scope values with a space in the authorization request, ensuring users only hand over necessary data.
*   **Restrictive Scopes:** To build user trust and maximize privacy, developers can request minimal scopes. For example, `profile-only` restricts the application's access solely to the `/current_user.json` endpoint, while `carts-only` limits access exclusively to `/carts/*.json` endpoints (allowing a third-party pattern store to process checkouts without seeing a user's stash or messages).
*   **Social and Communications:** Applications that need to interact with community content must request `forum-write` to create, edit, or delete forum posts, and `message-write` to send and delete private direct messages. 
*   **The Copyright Security Boundary (`library-pdf`):** One of the strictest security boundaries involves the `library-pdf` scope, which allows an application to directly generate download links for copyrighted pattern PDFs from a user's library. Because this deals with sensitive commercial material, **tokens requesting the `library-pdf` scope expire much faster than standard tokens**. Access can also be instantly revoked if the application exceeds the strict rate limit of 100 requests per day. Ravelry advises developers to hold two separate tokens for a user—a normal token for general API use and a dedicated `library-pdf` token—to prevent the entire application from breaking if the PDF token expires.

### 4. Environment Configuration and Deployment Safety
Properly setting up the deployment environment is critical to maintaining both security and connectivity within the ecosystem.
*   **Securing Credentials:** SDKs and libraries are built to read API keys from hidden environment variables rather than hardcoded text. For example, the `ravelRy` R package looks for `RAVELRY_USERNAME` and `RAVELRY_PASSWORD` in a local `.Renviron` file, while the `MCP_ravelry` server requires credentials to be stored in secure `.env.development` and `.env.production` files.
*   **Framework Best Practices (Laravel):** When deploying PHP frameworks like Laravel to live servers, storing API URLs and credentials directly in `.env` files can cause caching conflicts. Developers are advised to map these environment variables into a dedicated configuration file (e.g., `/config/ravelry_api.php`) and access them using Laravel's `config()` helper instead of `env()`. This ensures that when the server runs optimization commands like `artisan config:cache`, the credentials are read correctly from the cache, preventing unexpected connection failures.

### 5. Operational Safety, Rate Throttling, and Troubleshooting
The Ravelry API ecosystem relies heavily on developers adhering to operational safety guidelines to maintain platform stability.
*   **Terms of Use:** Developers must agree to Terms of Service prohibiting any automated traffic that disrupts server architectures or compromises user confidentiality. The platform actively monitors traffic and will immediately suspend API access keys if malicious patterns are detected, directing all abuse reports to `abuse@ravelry.com`.
*   **Dynamic Rate Limiting:** To prevent server overload, Ravelry does not use rigid time windows (e.g., 100 requests per hour); instead, it evaluates request velocity dynamically. High-throughput scripts must actively monitor response headers like `x-ratelimit-limit` and `x-ratelimit-remaining`. If a script hits the threshold, the API returns an **HTTP 429 Too Many Requests** error, at which point the application must implement exponential backoff algorithms and robust retry-after parsing to pause execution.
*   **Troubleshooting the Cryptic "500 Error":** A notorious setup pitfall for data scientists using Basic Auth (such as via R's `httr` library) involves encountering an **HTTP 500 Internal Server Error** instead of the expected 401 Unauthorized error. If a developer stores their credentials in a local text file (e.g., `user_rav.txt`) but makes a typo in the column headers or misaligns the formatting, Ravelry's server parsing engine crashes upon receiving the malformed authentication string. Correcting the local file format instantly resolves the server crash and allows authentication to proceed.
*   **Live Server Transport Leaks:** Occasionally, cURL requests that work perfectly on a local development machine will return `null` or `false` when pushed to a live production server. This often points to firewall restrictions, outbound port blocking, or hosting provider DNS conflicts failing to resolve `api.ravelry.com`.
