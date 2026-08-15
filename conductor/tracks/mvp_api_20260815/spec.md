# Specification: MVP API Functionality & History Tracking

## Overview
This track focuses on finishing the core minimum viable product (MVP) API functionality for StashStats. This includes creating the fundamental Pydantic models for Yarns, Stashes, and References, as well as implementing the App Data API client methods for tracking stash quantity history over time. The architecture will lean towards an independent object approach, paving the way for a future Model-View-Controller (MVC) setup in the web app.

## Functional Requirements
1. **Core Models**: Implement Pydantic models in `src/stashstats/models/` for:
   - Yarn (`Yarn`, `YarnFiber`, `Colorway`, `YarnDetailResponse`)
   - Stash (`StashItem`, `StashSearchResponse`, `StashDetailResponse`)
   - References (`ColorFamily`, `YarnWeightReference`, `FiberCategory`)
2. **History Models**: Implement models for tracking history in `src/stashstats/models/history.py` (`StashHistory`, `StashHistoryEntry`).
3. **App Data API Integration**: Implement client methods to interact with Ravelry's App Data Key-Value storage API for the history objects:
   - `get_app_data`, `set_app_data`, `delete_app_data`
   - `get_stash_history`, `get_batch_stash_history`
   - `record_stash_snapshot` (with auto-deduplication logic to only append if timestamp or quantity metrics differ from the latest entry)
   - `delete_stash_history`
4. **Architectural Independence**: Models and client logic should remain independent and decoupled, preparing for a Model-View-Controller orchestration layer in the future web application.

## Non-Functional Requirements
- **Data Validation**: Strict typing and validation using Pydantic.
- **Code Quality**: Conform to `Black` formatting and `Ruff` linting rules.

## Acceptance Criteria
- [ ] All specified Pydantic models are successfully created and correctly type-hinted.
- [ ] The client can successfully push and fetch App Data API history entries.
- [ ] History auto-deduplication logic correctly ignores identical successive quantity snapshots.
- [ ] All tests pass successfully.

## Out of Scope
- Frontend / Web Dashboard implementation.
- Complex analytics calculations (e.g., project velocity algorithms) beyond storing raw quantity history.
