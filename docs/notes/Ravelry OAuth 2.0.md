---
aliases:
  - "OAuth 2.0"
tags:
  - ravelry
  - documentation
---

# Ravelry OAuth 2.0

**OAuth 2.0 serves as the primary security and authentication gateway for distributed, multi-user applications within the Ravelry API ecosystem.** While data scientists and researchers typically utilize Basic Authentication to scrape public data or manage their personal accounts, OAuth 2.0 is strictly required for public-facing web and mobile client applications. This protocol ensures that end-users can securely log into their personal Ravelry accounts and grant third-party applications limited access without ever exposing their private passwords to the developer.

Here is a detailed overview of how OAuth 2.0 is structured and integrated into the Ravelry platform:

### 1. Core Endpoints and Architecture
Ravelry implements a standard three-legged OAuth 2.0 flow using two primary endpoints:
*   **Authorization Endpoint:** `https://www.ravelry.com/oauth2/auth`.
*   **Token Endpoint:** `https://www.ravelry.com/oauth2/token`.

When an application requests a token from the server, Ravelry enforces a specific architectural constraint regarding credential transmission: **it supports Basic Authentication (using the HTTP `Authorization` header) for passing the application's `client_id` and `client_secret`**. Conversely, "body auth"—the practice of submitting these credentials as standard form parameters in the body of the request—is explicitly not supported. 

### 2. Strict Security Validators
Ravelry’s OAuth 2.0 gateway relies on highly specific, strict validation constraints that developers must carefully navigate to avoid connection failures:
*   **The 8-Character `state` Requirement:** To prevent cross-site request forgery (CSRF), the API requires a `state` parameter during authorization. Crucially, this must be a secure, random string that is **strictly greater than eight characters in length**. If an application submits a state string that is eight characters or shorter, the server will immediately reject the request and the authorization flow will fail.
*   **No Out-of-Band (OOB) Support:** Ravelry does not support "Out-of-Band" authorization. This means third-party integrations cannot rely on a user manually copying and pasting an authorization code from a browser back into the app. Instead, the application must define a strict callback URL or a dedicated internal app scheme to catch the token redirects automatically.

### 3. Token Lifecycle and Expiration Management
Tokens generated via OAuth 2.0 have a rapid expiration cycle, **expiring completely in 24 hours**. 
*   **The `offline` Scope:** To maintain persistent access without forcing the end-user to re-enter their Ravelry credentials every single day, developers must explicitly request the `offline` scope. This grants the application a refresh token, allowing the OAuth client library to silently refresh the access token in the background before it expires. 
*   **Catching 401s:** Even with refresh tokens active, Ravelry requires applications to be engineered to gracefully handle HTTP **401 Unauthorized** responses. If a token naturally expires, hits a rate limit, or is manually revoked by the user, the application must automatically re-authenticate the user.

### 4. Granular Authorization Scopes (Permissions)
To protect user privacy, an OAuth 2.0 token does not grant blanket access to a user's entire Ravelry account by default. Applications must explicitly request specific "scopes" (permissions) to interact with protected features, separating multiple scopes with a space:
*   **Social & Communication:** Applications must request the `forum-write` scope to create, edit, or delete forum posts on the user's behalf. Similarly, the `message-write` scope is required to send and delete private direct messages.
*   **The `library-pdf` Security Boundary:** The `library-pdf` scope allows an application to directly generate download links for copyrighted pattern PDFs stored in a user's digital library. Because this deals with sensitive commercial material, **tokens requesting the `library-pdf` scope expire much faster than standard tokens**. Furthermore, access can be instantly revoked if the application exceeds the daily download rate limit, which is strictly capped at 100 requests per day. Ravelry's official documentation advises developers to hold two separate tokens for a single user—a normal token for general API use and a dedicated `library-pdf` token—to prevent the entire application from breaking if the PDF token prematurely expires.
*   **Restrictive Scopes:** To build trust and maximize privacy, developers can request highly restrictive scopes. For example, `profile-only` limits the app's access entirely to the `/current_user.json` endpoint. The `carts-only` scope limits access strictly to `/carts/*.json` endpoints; this is ideal for external pattern websites that want to process checkouts and add purchased items to a user's Ravelry library without ever gaining access to their private messages or stash data.

### 5. Ecosystem Support and Developer Tooling
Because implementing OAuth 2.0 flows from scratch can be highly complex, the Ravelry developer community has built specific open-source libraries and tools to handle these requirements:
*   **PHP Integrations:** In the PHP ecosystem, the `ravelry-oauth2` library serves as a functional prototype explicitly designed to demonstrate and manage Ravelry's dynamic OAuth 2.0 authorization redirects. Another comprehensive library, `theloopyewe-ravelry-api.php`, includes a dedicated `OauthTokenStorage` handler that seamlessly manages the access and secret keys required to authenticate API calls for distributed apps.
*   **Mobile Testing (Kotlin/Android):** For mobile developers building Android applications, repositories like the Kotlin-based `retroravelry` provide dedicated Postman collections (e.g., `ravelry_postman_collection.json`). This allows developers to browse the REST API visually and quickly generate mock OAuth 2.0 access tokens to safely test their integration code before pushing the application to production.
