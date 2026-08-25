# Plan: Project PDF Upload

## Phase 1: Storage & Serving Layer

- [ ] Task: Add `save_project_pdf` utility to `storage.py` — writes PDF bytes to `data/<user_id>/projects/pdfs/<project_id>/` [#]
- [ ] Task: Add `list_project_pdfs` utility — returns list of filenames for a given user+project [#]
- [ ] Task: Add `delete_project_pdf` utility — removes a named PDF from disk [#]
- [ ] Task: Register Dash server route `/projects/pdf/<user_id>/<project_id>/<filename>` in `web/app.py` that streams PDF bytes [#]
- [ ] Task: Write unit tests for all three storage utilities (save, list, delete) [#]
- [ ] Task: Write integration test for the serve route (mock filesystem, verify response headers) [#]
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md) [#]

## Phase 2: Projects Tab Layout

- [ ] Task: Replace "Projects coming soon." stub in `layouts/main.py` with a real Projects tab layout component in `layouts/projects.py` [#]
- [ ] Task: `layouts/projects.py` — `create_projects_layout()` renders a placeholder grid/list; each project row includes `dcc.Upload` zone (accept=`application/pdf`) and a file list container [#]
- [ ] Task: Add `dcc.Store` (`projects-pdf-store`) for client-side file list state per project [#]
- [ ] Task: Write unit/render tests for `create_projects_layout()` (snapshot-style: verify key component IDs exist) [#]
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md) [#]

## Phase 3: Upload & Delete Callbacks

- [ ] Task: Add `callbacks/projects.py` with `register_projects_callbacks(app)` [#]
- [ ] Task: Implement upload callback — decode base64 dcc.Upload payload, validate MIME type (PDF only) and size (≤25 MB), call `save_project_pdf`, update file list store, display error on rejection [#]
- [ ] Task: Implement list-load callback — on Projects tab activation, load file lists from filesystem for all visible projects and populate stores [#]
- [ ] Task: Implement delete callback — on delete button click, call `delete_project_pdf`, refresh file list [#]
- [ ] Task: Implement viewer callback — on filename selection, set iframe `src` to the serve route URL [#]
- [ ] Task: Register `register_projects_callbacks` in `web/app.py` alongside existing callback registrations [#]
- [ ] Task: Write unit tests for upload callback (valid PDF, oversized PDF, non-PDF, successful save) [#]
- [ ] Task: Write unit tests for delete callback [#]
- [ ] Task: Write unit tests for viewer callback [#]
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md) [#]

## Phase 4: Components & Styling

- [ ] Task: Add `components/projects.py` — `create_pdf_file_list(filenames, project_id)` renders filename buttons + delete buttons per file [#]
- [ ] Task: Add `components/projects.py` — `create_pdf_viewer(src_url)` renders `html.Iframe` with correct styles (height 600px, width 100%) [#]
- [ ] Task: Wire file list component into layout and callbacks [#]
- [ ] Task: Write render tests for both new component functions [#]
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md) [#]
