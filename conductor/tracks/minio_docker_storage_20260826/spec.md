# Spec: Docker Compose Consolidation & MinIO Storage

## Overview
Consolidate the legacy web dev/prod Docker Compose setup into a single unified `app` service. Introduce a dedicated MinIO container (S3-compatible) to handle project PDF storage, bypassing local filesystem constraints and providing scalable object storage, since Ravelry's API does not support native PDF uploads for projects.

## Functional Requirements
- **Docker Compose Cleanup**: Remove outdated `web-dev` and `web-prod` references, ports, and environment variables. Establish `app` as the single web service.
- **MinIO Integration**: Add a MinIO service to `docker-compose.yml`.
- **Auto-Provisioning**: Include a MinIO setup container/script (using `mc`) to automatically provision a default bucket (`stashstats-pdfs`) and configure access policies on startup.
- **Storage Code Refactor**: Update Python storage backend (`src/stashstats/storage.py`) to use S3/MinIO API (via `boto3` or `minio-py`) for saving, listing, and deleting project PDFs.
- **User Tracking & Object Keys**: Maintain multi-tenant isolation by structuring MinIO object keys as `<user_id>/projects/pdfs/<project_id>/<filename>.pdf`. This mirrors the previous local folder structure and ensures PDFs are scoped to the user who uploaded them.
- **Web App Routing**: Update the web app PDF serve route to fetch and stream PDFs from the MinIO bucket using the structured object keys.

## Non-Functional Requirements
- **Configuration**: MinIO credentials (endpoint, access key, secret key, bucket name) must be configured via `.env` and loaded securely.
- **Resilience**: The `app` service should depend on MinIO being healthy/ready.

## Acceptance Criteria
- `docker-compose up` cleanly starts the `app`, `cache`, and `minio` (with auto-provisioned bucket).
- Users can upload a PDF in the web UI and it successfully lands in the MinIO bucket at the correct `<user_id>/...` path.
- Users can view and delete uploaded PDFs from the UI, with changes reflected in MinIO.
- No local filesystem artifacts (`data/`) are created for PDFs.
- All stale dev/prod references in `docker-compose.yml` and `.env.example` are removed.

## Out of Scope
- Migrating existing local PDFs to MinIO (users will need to re-upload or a separate migration script will be handled later).
- Advanced MinIO features like distributed mode, TLS, or external public access (internal Docker network access is sufficient for the `app`).
