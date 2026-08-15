---
title: Stash Data Model
created: 2026-08-14
updated: 2026-08-14
type: entity
tags: [model, stash, yarn]
sources: [raw/articles/ravelry-api-reference.md, src/stashstats/models/stash.py]
confidence: high
---

# Stash Data Model

The Ravelry API defines multiple representations of user stash objects depending on context.

## Stash Object Variants
1. **`Stash (list)`** *(Most frequently returned)*: Primary summary record returned by `GET /people/{username}/stash/list.json`, `GET /people/{username}/stash/comments.json`, and `/stash/search.json`. Implemented in `stashstats.models.StashItem`.
2. **`Stash (small)`**: Minimal representation without user or custom yarn weight metadata.
3. **`Stash (list_with_notes)`**: Includes `notes` and `notes_html` text fields.
4. **`Stash (full)`**: Complete detail record returned by `GET /people/{username}/stash/{id}.json` containing full `packs: list[Pack]` and `photos: list[Photo]` arrays.
5. **`Stash (full_for_owner)`**: Full record augmented with private owner properties.
6. **`Stash (export)`**: Format optimized for bulk data export.
7. **`Stash (POST)`**: Input payload structure for creating and modifying stash records via `POST /people/{username}/stash/create.json`.

## Official `Stash (list)` Schema (`StashItem`)

| Attribute | Type | Nullable | Description |
|---|---|---|---|
| `id` | `Integer` | No | Unique stash item record ID |
| `name` | `String` | Yes | User-added yarn title |
| `permalink` | `String` | No | URL slug for stash entry |
| `colorway_name` | `String` | Yes | Colorway name or number |
| `color_family_name`| `String` | Yes | Standard color family grouping |
| `dye_lot` | `String` | Yes | Dye lot identifier |
| `location` | `String` | Yes | Storage location description |
| `comments_count` | `Integer` | No | Number of user comments |
| `favorites_count` | `Integer` | No | Total user favorites |
| `handspun` | `Boolean` | No | Whether yarn is handspun fiber |
| `has_photo` | `Boolean` | Yes | Photo presence flag |
| `created_at` | `Date/String` | Yes | Creation timestamp |
| `updated_at` | `Date/String` | Yes | Last modification timestamp |
| `tag_names` | `Array[String]` | No | List of user tags |
| `yarn_weight_name` | `String` | Yes | Name of yarn weight (e.g., 'Worsted') |
| `long_yarn_weight_name` | `String` | Yes | Long description of yarn weight |
| `personal_yarn_weight` | `YarnWeight` | Yes | Custom weight if unlinked |
| `stash_status` | `StashStatus` | Yes | Active status (`In stash`, `Used up`, etc.) |
| `yarn` | `StashYarn` | Yes | Linked [[yarn-model]] record |
| `primary_pack` | `Pack` | Yes | Primary [[pack-model]] holding skeins & yardage |
| `first_photo` | `Photo` | Yes | Primary representative photo |
| `user` | `UserProfile` | Yes | [[user-model]] of the stash owner |

---

## Cross-References
- [[api-stash]]: Stash API endpoints.
- [[yarn-model]]: Catalog yarn specification.
- [[pack-model]]: Skein batch allocations.
- [[user-model]]: User profile representation.
- [[module-client]]: Client methods consuming this model.
