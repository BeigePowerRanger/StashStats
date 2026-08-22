---
title: Input Objects and POST Data
created: 2026-08-14
updated: 2026-08-14
type: concept
tags: [endpoint, protocol]
sources: [raw/articles/ravelry-api-reference.md]
confidence: high
---

# Input Objects and POST Data

The Ravelry API supports multiple formats for sending create and update payloads.

## Payload Submission Methods

Methods specifying a parameter named `data` (e.g. `TypeName#POST` objects):

1. **Raw JSON Body (Recommended)**:
   ```http
   POST /people/username/stash/create.json HTTP/1.1
   Content-Type: application/json

   {
     "yarn_id": 1234,
     "colorway_name": "Autumn Hues",
     "skeins": 3
   }
   ```
2. **Form-Encoded with `data` parameter**:
   `POST data={"yarn_id": 1234, "colorway_name": "Autumn Hues"}`
3. **Flat Name/Value Pairs**:
   `POST yarn_id=1234&colorway_name=Autumn+Hues` (Note: nested attributes cannot be represented flat).

---

## Related
- [[auth-and-permissions]]
- [[api-stash]]
- [[api-projects-and-queue]]
- [[stash-model]]
