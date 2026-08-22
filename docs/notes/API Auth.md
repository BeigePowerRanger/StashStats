## Accessing Ravelry with HTTP Basic Auth: read only access

If you only need to use read-only API methods, read-only Basic Auth is the simplest way to get started.

When you use your read-only credentials, you will only be able to call API methods that are not marked as "authenticated" in the documentation.

Use HTTP Basic Authentication with your HTTP client and supply the username and password taken from your app's credentials. SSL is required.

Example:  

> `curl -u _basic_auth_username_:_basic_auth_password_ https://api.ravelry.com/current_user.json`

## Authenticating via HTTP Basic Auth: personal account access

If you only need to sign in to Ravelry as yourself, you can use this simple method to access the API. You do not have to request specific permissions when authenticating this way - all permissions are granted.

Use HTTP Basic Authentication with your HTTP client and supply your access key as the username and your personal key (not your secret key) as the password. Note that SSL is required: you will receive a 403 error if you do not use HTTPS.

IMPORTANT: "Basic Auth: personal account access" credentials provide **full access to the Ravelry account that they are associated with.** This is intended for personal projects.

A quick example:  

> `curl -u _basic_auth_username_:_basic_auth_personal_key_ https://api.ravelry.com/current_user.json`

## Authenticating with Ravelry via OAuth 2.0

Use your client ID and client secret to authenticate with Ravelry using any [OAuth 2 library](http://oauth.net/code/).

The OAuth 2 URLs are:

- https://**www**.ravelry.com/oauth2/token
- https://**www**.ravelry.com/oauth2/auth

See "OAuth scope" below for information on requesting specific permissions.

**When requesting your token, we support basic auth** (the "Authorization" header) for passing your client ID and secret. Submitting these as form parameters (also called "body auth") is not supported.

OAuth 2 tokens expire in 24 hours. You will probably want to request the "offline" scope so that you can receive a refresh token. Your OAuth client library should allow you to refresh your access token before it expires so that you do not have to re-authorize. Your application should handle HTTP 401 Unauthorized responses by re-authenticating the user.

## Authenticating with Ravelry via OAuth 1.0a

Use your consumer key and consumer secret authenticate with Ravelry using any [OAuth 1.0a library](https://oauth.net/1/).

The OAuth URLs are:

- https://**www**.ravelry.com/oauth/request_token
- https://**www**.ravelry.com/oauth/access_token
- https://**www**.ravelry.com/oauth/authorize

See "OAuth scope" below for information on requesting specific permissions.

OAuth tokens are long-lived but they can expire after a period of inactivity or if the user revokes access. **Your application should handle HTTP 401 Unauthorized** responses by re-authenticating the user.

## OAuth scopes (permissions)

The OAuth `request_token` and OAuth 2 `token` methods accept an optional "scope" parameter. Use this parameter when your application needs to request additional privileges that aren't granted by default. To request several privileges, separate the values with a space.

If you are using a personal key instead of OAuth, you do not need to request specific permissions.

### Standard Scopes

|Key|Description|
|---|---|
|offline|_standard OAuth 2.0 scope for requesting refresh tokens_|
|deliveries-read|list the products that have been purchased by or gifted to the current user|
|forum-write|create, edit, and delete forum posts|
|library-pdf|directly download PDFs from a user's library using [generate_download_link](https://www.ravelry.com/api#product_attachments_generate_download_link). **note:** tokens that request this scope will expire more quickly than usual and may also expire if a rate limit is exceeded. You may want to hold both a normal token and a library-pdf token for each user when this permission is requested.|
|pattern-write|_not currently available to third-party apps_|
|patternstore-read|enumerate the pattern stores that the user administers as well as the products within those stores|
|patternstore-write|_not currently available to third-party apps_|
|profile-write|allow profile updating|

### Limited availability scopes

|Key|Description|
|---|---|
|message-read|_currently limited access, available by request. View a user's private messages_|
|pattern-write|_not currently available to third-party apps_|
|patternstore-purchases|_currently limited access, available to individual designers by request_|
|patternstore-write|_not currently available to third-party apps_|
|patternstore-pdf|_currently limited access, available by request. Generate download links for PDF files within the user's pattern stores_|

### Minimal Scopes

There are also scopes which allow you to select a minimal set of privileges.

|Key|Description|
|---|---|
|profile-only|allows access to /current_user.json and nothing else|
|carts-only|allows access to /carts/*.json and nothing else|