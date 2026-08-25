# Implementation Plan: Prod/Dev Scaffolding & Multi-User API Storage

## Phase 1: Environment Variables Updates [checkpoint: b5cd93a]
- [x] Task: Update Environment Templates [e18665e]
  - [x] Remove `RAVELRY_USERNAME` and `DATABASE_URL` from `.env.example`.
  - [x] Add `DEV_USERNAME`, `DEV_API_KEY`, `PROD_USERNAME`, and `PROD_API_KEY` to `.env.example`.
- [x] Task: Update Application Configuration [e18665e]
  - [x] Ensure application config validation (e.g., Pydantic settings) is updated to require/support the new DEV/PROD environment variables.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [b5cd93a]

## Phase 2: Docker Compose Stack Refactor
- [ ] Task: Refactor Dev Service
  - [ ] Rename `web` to `web_dev` in `docker-compose.yml`.
  - [ ] Verify `web_dev` remains accessible via local host ports.
- [ ] Task: Introduce Prod Service
  - [ ] Add `web_prod` service to `docker-compose.yml`.
  - [ ] Configure `web_prod` to build from the remote git repository `main` branch.
- [ ] Task: Introduce Tailscale Sidecar
  - [ ] Add `stashstats-tailscale` service to `docker-compose.yml`.
  - [ ] Configure the sidecar to route traffic securely to `web_prod` over the tailnet without exposing public host ports.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Multi-User Data Storage Refactor
- [ ] Task: Write Tests for Multi-User Storage
  - [ ] Write tests ensuring that data reads/writes route to `app/data/<user_id>/` instead of a global path.
- [ ] Task: Refactor Storage Logic
  - [ ] Update `app/data` read/write functions to accept and namespace via `user_id`.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
