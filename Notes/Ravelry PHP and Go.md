---
aliases:
  - "PHP & Go"
tags:
  - ravelry
  - documentation
---

# Ravelry PHP and Go

**Within the Ravelry API ecosystem, PHP and Go primarily serve as architectural engines for building backend web applications, custom storefront integrations, and high-performance microservices.** While languages like R and Python dominate data science and local automation, PHP and Go provide the server-side infrastructure required to bridge external websites and compiled tools with Ravelry's databases.

### 1. The PHP Ecosystem: Web Frameworks and Dedicated Libraries
PHP developers have built specific open-source libraries to handle the complexities of Ravelry's nested JSON payloads, strict authentication rules, and web framework integrations.

*   **Authentication Prototypes:** The **`jriede/ravelry-oauth2`** project acts as a functional prototype library specifically designed to demonstrate and manage Ravelry's dynamic OAuth 2.0 authorization redirects within a PHP environment.
*   **Comprehensive API Consumption:** A more robust solution is the **`dpb587/theloopyewe-ravelry-api.php`** library, which relies on Composer for dependency management. This library seamlessly handles both major authentication modalities: it utilizes an `OauthTokenStorage` handler for distributed OAuth apps, and supports standard Access/Personal keys for HTTP Basic Authentication. When an API call is made, this library parses the response so the developer can cleanly interact with the data as either a traversable array or an internal object. The library also maintains strict functional tests via PHPUnit, which require a dedicated test account to safely validate live API responses without corrupting the developer's primary data.
*   **Laravel Integration and Production Troubleshooting:** PHP is frequently utilized to weave Ravelry API data—such as knitting patterns—directly into custom web frameworks like Laravel. Developers often utilize raw cURL requests to retrieve these JSON files. However, deploying these PHP applications to live production servers frequently introduces environmental bugs. A common point of failure occurs when firewall configurations block the outbound request, or hosting provider DNS conflicts fail to resolve `api.ravelry.com`. When this happens, `curl_exec` returns `false` or `null` instead of a JSON payload, causing the PHP application to crash with a "Trying to get property of non-object" error during the `json_decode` process. 
*   **Configuration Best Practices:** To prevent configuration errors in production, Laravel developers are advised to store API credentials in dedicated setup files (like `/config/ravelry_api.php`) and call them using the `config()` helper rather than directly calling `env()` variables throughout the code. This ensures that when the server runs optimization commands like `artisan config:cache`, the credentials are read correctly from the cache, preventing unexpected connection failures.

### 2. The Go Ecosystem: High-Performance Backend SDKs
For compiled backend services, the Go programming language relies on the unofficial **`go-ravelry`** SDK created by developer CamiloGarciaLaRotta. Within the broader API ecosystem, this SDK occupies a highly specific niche: it is structurally focused on global taxonomy rather than personal user content.

*   **Master Database Coverage:** The `go-ravelry` SDK successfully implements Ravelry's core reference endpoints. It provides full support for authenticating the `current_user` and querying foundational databases like `color_families`, `yarn_weights`, `yarn_attributes`, `fiber_categories`, and basic searches. 
*   **Intentional Limitations:** Unlike Python automation scripts or mobile wrappers that manage a crafter's "Notebook," the Go SDK explicitly excludes personal inventory management. According to its roadmap, features like the user's Stash, Queue, Projects, Library, and private Messages are entirely unimplemented and marked as out-of-scope. 
*   **Architectural Role:** Because of these boundaries, the `go-ravelry` SDK is best suited for building fast, compiled backend microservices that need to validate credentials or reference standardized crafting metrics (like identifying specific metric yarn thicknesses or textile properties), rather than building complete client applications that synchronize user data.
