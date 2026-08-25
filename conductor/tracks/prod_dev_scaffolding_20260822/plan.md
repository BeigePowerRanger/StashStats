# Implementation Plan: Prod/Dev Scaffolding & Multi-User API Storage

## Phase 1: Environment Variables Updates [checkpoint: b5cd93a]
- [x] Task: Update Environment Templates [e18665e]
  - [x] Remove `RAVELRY_USERNAME` and `DATABASE_URL` from `.env.example`.
  - [x] Add `DEV_USERNAME`, `DEV_API_KEY`, `PROD_USERNAME`, and `PROD_API_KEY` to `.env.example`.
- [x] Task: Update Application Configuration [e18665e]
  - [x] Ensure application config validation (e.g., Pydantic settings) is updated to require/support the new DEV/PROD environment variables.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [b5cd93a]

## Phase 2: Docker Compose Stack Refactor
- [x] Task: Refactor Dev Service [f145d47]
  - [x] Rename `web` to `web_dev` in `docker-compose.yml`.
  - [x] Verify `web_dev` remains accessible via local host ports.
- [x] Task: Introduce Prod Service [f145d47]
  - [x] Add `web_prod` service to `docker-compose.yml`.
  - [x] Configure `web_prod` to build from the remote git repository `main` branch.
- [x] Task: Introduce Tailscale Sidecar [f145d47]
  - [x] Add `stashstats-tailscale` service to `docker-compose.yml`.
  - [x] Configure the sidecar to route traffic securely to `web_prod` over the tailnet without exposing public host ports.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Multi-User Data Storage Refactor
- [x] Task: Write Tests for Multi-User Storage [d45662c]
  - [x] Write tests ensuring that data reads/writes route to `app/data/<user_id>/` instead of a global path.
- [x] Task: Refactor Storage Logic [c3fab41]
  - [x] Update `app/data` read/write functions to accept and namespace via `user_id`.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
