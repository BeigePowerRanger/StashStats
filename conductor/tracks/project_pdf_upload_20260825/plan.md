# Plan: Project PDF Upload

## Phase 1: Storage & Serving Layer [checkpoint: 8394b4a]

- [x] Task: Add `save_project_pdf` utility to `storage.py` — writes PDF bytes to `data/<user_id>/projects/pdfs/<project_id>/` [d2e494b]
- [x] Task: Add `list_project_pdfs` utility — returns list of filenames for a given user+project [d2e494b]
- [x] Task: Add `delete_project_pdf` utility — removes a named PDF from disk [d2e494b]
- [x] Task: Register Dash server route `/projects/pdf/<user_id>/<project_id>/<filename>` in `web/app.py` that streams PDF bytes [d2e494b]
- [x] Task: Write unit tests for all three storage utilities (save, list, delete) [d2e494b]
- [x] Task: Write integration test for the serve route (mock filesystem, verify response headers) [d2e494b]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [8394b4a]

## Phase 2: Projects Tab Layout [checkpoint: 2c4f7d4]

- [x] Task: Replace "Projects coming soon." stub in `layouts/main.py` with a real Projects tab layout component in `layouts/projects.py` [d2e494b]
- [x] Task: `layouts/projects.py` — `create_projects_layout()` renders a placeholder grid/list; each project row includes `dcc.Upload` zone (accept=`application/pdf`) and a file list container [d2e494b]
- [x] Task: Add `dcc.Store` (`projects-user-store`) for client-side file list state per project [d2e494b]
- [x] Task: Write unit/render tests for `create_projects_layout()` (snapshot-style: verify key component IDs exist) [d2e494b]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [2c4f7d4]

## Phase 3: Upload & Delete Callbacks

- [x] Task: Add `callbacks/projects.py` with `register_projects_callbacks(app)` [d2e494b]
- [x] Task: Implement upload callback — decode base64 dcc.Upload payload, validate MIME type (PDF only) and size (≤25 MB), call `save_project_pdf`, update file list store, display error on rejection [d2e494b]
- [x] Task: Implement list-load callback — on Projects tab activation, load file lists from filesystem for all visible projects and populate stores [d2e494b]
- [x] Task: Implement delete callback — on delete button click, call `delete_project_pdf`, refresh file list [d2e494b]
- [x] Task: Implement viewer callback — on filename selection, set iframe `src` to the serve route URL [d2e494b]
- [x] Task: Register `register_projects_callbacks` in `web/app.py` alongside existing callback registrations [d2e494b]
- [x] Task: Write unit tests for upload callback (valid PDF, oversized PDF, non-PDF, successful save) [d2e494b]
- [x] Task: Write unit tests for delete callback [d2e494b]
- [x] Task: Write unit tests for viewer callback [d2e494b]
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Components & Styling

- [x] Task: Add `components/projects.py` — `create_pdf_file_list(filenames, project_id, user_id)` renders filename buttons + delete buttons per file [d2e494b]
- [x] Task: Add `components/projects.py` — `create_pdf_viewer(src_url)` renders `html.Iframe` with correct styles (height 600px, width 100%) [d2e494b]
- [x] Task: Wire file list component into layout and callbacks [d2e494b]
- [x] Task: Write render tests for both new component functions [d2e494b]
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
