# Subtrack Specification: Phase 1 - Reference and Yarn Models

## Overview
Implement, validate, and test Pydantic models representing Ravelry Reference taxonomy (`color_families`, `yarn_weights`, `fiber_categories`) and Yarn data structures (`yarns`, `yarn_fibers`, `colorways`, search/detail responses).

## Functional Requirements
1. **Reference Models (`src/stashstats/models/reference.py`)**:
   - `ColorFamily`: `id`, `name`, `permalink`, `spectrum_order` (optional).
   - `YarnWeightReference`: `id`, `name`, `ply`, `wpi`, `min_gauge`, `max_gauge`, `crochet_gauge`.
   - `FiberCategory`: `id`, `name`, `permalink`.
   - Response envelopes for reference listing endpoints if needed.

2. **Yarn Models (`src/stashstats/models/yarn.py`)**:
   - `YarnWeight`: taxonomy specs embedded in yarn objects.
   - `FiberType`: ID, name, animal_fiber, synthetic, vegetable booleans.
   - `YarnFiber`: ID, percentage, nested `FiberType`.
   - `Colorway`: ID, name, `color_family_id`.
   - `Yarn`: full commercial yarn details with `photos`, `yarn_fibers`, `yarn_company`, ratings, care instructions.
   - `YarnSearchResult` & `YarnSearchResponse`: paginated search results.
   - `YarnDetailResponse`: `{"yarn": Yarn}` envelope.

3. **Validation & Deserialization Tests**:
   - `tests/models/test_reference.py`: Deserialization of sample payloads, null handling, type coercion.
   - `tests/models/test_yarn.py`: Deserialization of sample Ravelry API responses for search results and yarn details.

## Acceptance Criteria
- [ ] All reference models pass strict type validation.
- [ ] All yarn models correctly deserialize real/mock Ravelry JSON payloads without validation errors.
- [ ] 100% test pass rate with `pytest tests/models/`.
- [ ] Lint check passes with `ruff check`.
