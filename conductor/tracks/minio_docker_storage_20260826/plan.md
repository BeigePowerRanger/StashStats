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

## Phase 2: Python Storage Backend Refactor (MinIO API)
- [ ] Task: Update `requirements.txt` / dependencies (if applicable) to include `minio` or `boto3`
- [ ] Task: Write tests for MinIO storage backend (TDD)
    - [ ] Test uploading a PDF to MinIO with `<user_id>` object key structure
    - [ ] Test listing PDFs for a project from MinIO
    - [ ] Test deleting a PDF from MinIO
- [ ] Task: Refactor `src/stashstats/storage.py`
    - [ ] Initialize MinIO client using `.env` credentials
    - [ ] Rewrite `save_project_pdf` to put object to MinIO
    - [ ] Rewrite `list_project_pdfs` to list objects from MinIO with prefix
    - [ ] Rewrite `delete_project_pdf` to remove object from MinIO
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Web App Routing & Integration
- [ ] Task: Write tests for PDF streaming route
    - [ ] Test that `/projects/pdf/<user_id>/<project_id>/<filename>` returns PDF bytes from MinIO
- [ ] Task: Refactor `src/stashstats/web/app.py`
    - [ ] Update the PDF serving route to fetch the object from MinIO and stream it back via Flask/Dash response
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
