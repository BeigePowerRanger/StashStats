---
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
