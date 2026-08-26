# Spec: Pydantic Models & OOP Architecture Refactoring

## Overview
Elevate the codebase to modern Pydantic v2 patterns and a clean, modular Object-Oriented architecture. Replace loose dictionary manipulations and defensive fallback chains with strictly validated models, decompose the monolithic `RavelryClient` into domain mixins/services, and leverage Pydantic features (`Field`, `@field_validator`, `@computed_field`, `Literal`).

## Functional Requirements

### 1. Model Enhancements & Field Validation
- **`Photo` URLs**: Validate `*_url` fields using regex/validator ensuring valid web URL formats while retaining string serialization compatibility.
- **`StashHistoryEntry`**: Validate `timestamp` format (`YYYY/MM/DD HH:MM:SS ±HHMM`) using `@field_validator`. Enforce non-negative numeric constraints on `skeins`, `grams`, `yards`, `total_grams`, `total_yards` using `Field(ge=0)`. Convert `datetime` `@property` to `@computed_field`.
- **`StashDeltaEvent`**: Enforce `event_type: Literal["initial", "consumed", "acquired", "neutral"]`. Convert `datetime` to `@computed_field`.
- **`Project` Models**: Enforce `Literal` options for `status_name` and `craft_name`. Constrain `progress` to `Field(ge=0, le=100)`.

### 2. Client Decomposition & OOP Architecture
- **Decompose `RavelryClient`**: Break the 800+ line God class into focused domain mixin modules under `stashstats/client/` or mixins:
  - `YarnClientMixin`: `search_yarns`, `get_yarn_details`, `get_yarn_weight_categories`.
  - `StashClientMixin`: `search_stash`, `get_stash_items`, `get_stash_item`, `create_stash_item`, `update_stash_item`, `delete_stash_item`, packs & photo management.
  - `ProjectClientMixin`: `list_projects`, `get_project`, `create_project`, `update_project`, `delete_project`.
  - `AppDataClientMixin`: `get_app_data`, `set_app_data`, `get_stash_history`, `save_stash_history`.
  - `ReferenceClientMixin`: `get_color_families`, `get_crafts`, `get_project_statuses`.
- **Maintain Full Backward Compatibility**: `from stashstats.client import RavelryClient` must retain all existing public method signatures.
- **`Literal` Sort Types**: Use `Literal` for query sort parameters.

### 3. Analytics & Callbacks Pydantic Adoption
- **Analytics Typing**: Replace unvalidated `dict` indexing and `_safe_get` helper in `stashstats/analytics/projects.py` and `velocity.py` with validated Pydantic model calls.
- **Callbacks Cleanliness**: Replace raw dictionary literals in `web/callbacks/manual_yarn.py` and `web/callbacks/search.py` with typed Pydantic models.

## Acceptance Criteria
- All 339+ tests pass without regression.
- New unit tests verifying model validation, timestamp validator, and modular client mixins pass.
- Code coverage is maintained above 80%.
