# Plan: Pydantic Models & OOP Architecture Refactoring

## Phase 1: Pydantic Model Validation & Typing Hardening [checkpoint: f889470]
- [x] Task: Update `Photo` model with URL validation [073f187]
- [x] Task: Update `StashHistoryEntry` with timestamp `@field_validator`, `Field(ge=0)`, and `@computed_field` [073f187]
- [x] Task: Update `StashDeltaEvent` with `Literal` event types and `@computed_field` [073f187]
- [x] Task: Update `Project` and `Settings` models with `Literal` / constrained fields [073f187]
- [x] Task: Write tests for new model validators and computed fields [073f187]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Client Modularization & Domain Mixins [checkpoint: 8601ff9]
- [x] Task: Create domain mixins for `RavelryClient` (`YarnClientMixin`, `StashClientMixin`, `ProjectClientMixin`, `AppDataClientMixin`, `ReferenceClientMixin`) [5dbdecb]
- [x] Task: Update `RavelryClient` to inherit from domain mixins with `Literal` sort types [5dbdecb]
- [x] Task: Write unit tests verifying modular client mixins and method signatures [5dbdecb]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Analytics & Callbacks Pydantic Integration [checkpoint: 4313230]
- [x] Task: Refactor `analytics/projects.py` and `analytics/velocity.py` to enforce Pydantic model typing [4313230]
- [x] Task: Refactor synthetic item dictionary literals in `web/callbacks/manual_yarn.py` and `search.py` [4313230]
- [x] Task: Run full test suite and verify >80% coverage [4313230]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)
