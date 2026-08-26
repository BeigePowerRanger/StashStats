# Plan: Pydantic Models & OOP Architecture Refactoring

## Phase 1: Pydantic Model Validation & Typing Hardening
- [ ] Task: Update `Photo` model with URL validation
- [ ] Task: Update `StashHistoryEntry` with timestamp `@field_validator`, `Field(ge=0)`, and `@computed_field`
- [ ] Task: Update `StashDeltaEvent` with `Literal` event types and `@computed_field`
- [ ] Task: Update `Project` and `Settings` models with `Literal` / constrained fields
- [ ] Task: Write tests for new model validators and computed fields
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Client Modularization & Domain Mixins
- [ ] Task: Create domain mixins for `RavelryClient` (`YarnClientMixin`, `StashClientMixin`, `ProjectClientMixin`, `AppDataClientMixin`, `ReferenceClientMixin`)
- [ ] Task: Update `RavelryClient` to inherit from domain mixins with `Literal` sort types
- [ ] Task: Write unit tests verifying modular client mixins and method signatures
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Analytics & Callbacks Pydantic Integration
- [ ] Task: Refactor `analytics/projects.py` and `analytics/velocity.py` to enforce Pydantic model typing
- [ ] Task: Refactor synthetic item dictionary literals in `web/callbacks/manual_yarn.py` and `search.py`
- [ ] Task: Run full test suite and verify >80% coverage
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
