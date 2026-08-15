---
title: Library and Deliveries API
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, library, cart]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Library and Deliveries API

Manage digital patterns, purchased ebooks, and library volumes.

## Endpoints

- `GET /people/{username}/library/search.json`: Search and filter patterns/books in user's digital library.
- `GET /deliveries/list.json`: List digital purchases and gifts (requires `deliveries-read` scope).
- `POST /product_attachments/{id}/generate_download_link.json`: Generate secure temporary download link for PDF pattern files (requires `library-pdf` scope).

---

## Related
- [[pattern-model]]
- [[auth-and-permissions]]
- [[cart-and-product-models]]
