---
title: Carts and Stores API
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [endpoint, cart, store]
sources: [raw/articles/ravelry-api-reference.md]
confidence: medium
---

# Carts and Stores API

Endpoints for integrating third-party e-commerce stores with Ravelry's pattern purchasing and library delivery infrastructure.

## Endpoints

- `POST /carts/create.json`: Create a cart associated with a store ID.
- `POST /carts/{id}/add.json`: Add digital pattern products via item code (SKU).
- `POST /carts/{id}/external_checkout.json`: Notify Ravelry of external payment to trigger automatic library delivery to the buyer.

---

## Related
- [[cart-and-product-models]]
- [[auth-and-permissions]]
- [[api-library-and-deliveries]]
