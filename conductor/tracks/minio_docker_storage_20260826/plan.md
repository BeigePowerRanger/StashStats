# Plan: Docker Compose Consolidation & MinIO Storage

## Phase 1: Infrastructure Cleanup & MinIO Integration [checkpoint: 711295d]
- [x] Task: Update `docker-compose.yml` to remove legacy web dev/prod containers [9bb9658]
    - [x] Consolidate into a single `app` service
    - [x] Clean up outdated exposed ports and environment variables
- [x] Task: Add MinIO and MinIO setup (mc) services to `docker-compose.yml` [9bb9658]
    - [x] Configure MinIO container on port 9000
    - [x] Add `minio-create-bucket` ephemeral container to auto-provision `stashstats-pdfs` bucket and configure policies
- [x] Task: Update `.env.example` [9bb9658]
    - [x] Remove old dev/prod environment variables
    - [x] Add MinIO configuration variables (`MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Python Storage Backend Refactor (MinIO API) [checkpoint: a9bfc1f]
- [x] Task: Update `requirements.txt` / dependencies (if applicable) to include `minio` or `boto3` [f0f02c9]
- [x] Task: Write tests for MinIO storage backend (TDD) [f0f02c9]
    - [x] Test uploading a PDF to MinIO with `<user_id>` object key structure
    - [x] Test listing PDFs for a project from MinIO
    - [x] Test deleting a PDF from MinIO
- [x] Task: Refactor `src/stashstats/storage.py` [f0f02c9]
    - [x] Initialize MinIO client using `.env` credentials
    - [x] Rewrite `save_project_pdf` to put object to MinIO
    - [x] Rewrite `list_project_pdfs` to list objects from MinIO with prefix
    - [x] Rewrite `delete_project_pdf` to remove object from MinIO
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Web App Routing & Integration [checkpoint: a9bfc1f]
- [x] Task: Write tests for PDF streaming route [f0f02c9]
    - [x] Test that `/projects/pdf/<user_id>/<project_id>/<filename>` returns PDF bytes from MinIO
- [x] Task: Refactor `src/stashstats/web/app.py` [f0f02c9]
    - [x] Update the PDF serving route to fetch the object from MinIO and stream it back via Flask/Dash response
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)
