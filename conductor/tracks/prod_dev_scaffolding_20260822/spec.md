# Specification: Prod/Dev Scaffolding & Multi-User API Storage

## Overview
Refactor the current project scaffolding to support isolated development and production environments via Docker Compose. Update environment variable configurations to handle distinct credentials, add a Tailscale sidecar for secure internal access to the production container, and refactor the local `app/data` storage mechanism to support multiple users.

## Functional Requirements
1. **Environment Variables Updates:**
   - Remove global `RAVELRY_USERNAME` and `DATABASE_URL` from `.env` and `.env.example`.
   - Introduce `DEV_USERNAME`, `DEV_API_KEY`, `PROD_USERNAME`, and `PROD_API_KEY` for environment-specific authentication.
2. **Docker Compose Stack Refactor:**
   - Rename existing `web` service to `web_dev`.
   - Ensure `web_dev` remains accessible locally on the host machine.
   - Introduce a new `web_prod` service that builds directly from the remote Git repository `main` branch using Docker's remote git build context.
   - Introduce a `stashstats-tailscale` sidecar service to expose the `web_prod` application over a private Tailscale network (accessible via the tailnet).
3. **Multi-User Data Storage:**
   - Refactor the API data storage module to namespace data per user.
   - Ensure the new structure utilizes isolated subdirectories: `app/data/<user_id>/`.

## Non-Functional Requirements
- Ensure the Tailscale sidecar configuration does not expose public host ports inappropriately.
- No disruption to existing local development processes for `web_dev`.

## Acceptance Criteria
- `.env.example` successfully reflects the new DEV and PROD credential structure.
- `docker-compose.yml` successfully spins up `web_dev`, `web_prod`, and `stashstats-tailscale` services without port conflicts.
- `web_prod` successfully pulls and builds from the remote `main` branch and is accessible via the tailnet.
- `web_dev` remains accessible via localhost.
- API storage operations (read/write) correctly route to `app/data/<user_id>/`.

## Out of Scope
- Implementation of full user authentication/login UI.
