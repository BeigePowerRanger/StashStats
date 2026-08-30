# Spec: Project PDF Upload

## Overview
Users can attach one or more PDF files to a Ravelry project entry within the
Projects tab of StashStats. PDFs are optional — a project entry is fully valid
without any attached file. Uploaded PDFs are stored on the local filesystem in a
user-isolated directory and are accessible for inline viewing and individual
deletion without leaving the Projects tab.

## Functional Requirements

1. **Upload widget** — A `dcc.Upload` component is rendered per project card /
   row in the Projects tab. It accepts only `application/pdf` files. Upload is
   optional; the widget is visible at all times but not required to save/display
   a project.

2. **Storage** — PDFs are written to
   `data/<user_id>/projects/pdfs/<project_id>/` using the existing
   `storage.py` filesystem utilities. Each file is saved with its original
   filename (sanitised). On re-upload of a file with the same name the existing
   file is replaced.

3. **Multiple files** — A project entry can accumulate multiple distinct PDFs
   (e.g., multiple pattern PDFs, errata sheets). Each file is independently
   addressable.

4. **Delete** — Each listed file has an explicit delete button. Clicking it
   removes the file from disk and updates the displayed list.

5. **Display** — After upload (or on page load), the file list is shown below
   the upload widget. Selecting a filename opens an inline `html.Iframe` viewer
   that serves the PDF via a Dash `serve_layout`-style route (or equivalent
   local file serving endpoint). The iframe renders within the Projects tab.

6. **Serve endpoint** — A Dash server route (e.g.
   `/projects/pdf/<user_id>/<project_id>/<filename>`) streams the file bytes
   with `Content-Type: application/pdf` so the browser can render it inline.

7. **State persistence** — The list of attached files for a given project is
   re-derived from the filesystem on tab load, so it survives page refreshes.

## Non-Functional Requirements

- Max file size: 25 MB per PDF (enforced in callback, not at network layer).
- Filename sanitisation: strip path separators, null bytes; replace spaces with
  underscores.
- No auth beyond the existing user session; files are scoped to
  `<user_id>/<project_id>`.

## Acceptance Criteria

- [x] Projects tab shows a `dcc.Upload` zone per project; uploading a PDF saves
      the file and renders it in the file list.
- [x] Uploading a second PDF to the same project adds it to the list without
      removing the first.
- [x] Clicking the delete button for a file removes it from the list and from
      disk.
- [x] Selecting a filename in the list opens an inline iframe displaying the
      PDF.
- [x] Page refresh retains the file list derived from the filesystem.
- [x] Non-PDF uploads are rejected with a user-visible error message.
- [x] Files > 25 MB are rejected with a user-visible error message.
- [x] No upload is required to display/interact with a project entry.

## Out of Scope

- Cloud / object storage (S3, GCS).
- PostgreSQL BLOB storage.
- Full Projects CRUD (create/edit/delete project metadata) — the Projects tab
  stub is pre-existing; this track only adds PDF attachment to whatever project
  rows are already rendered.
- PDF text extraction or search.
- Sharing PDFs between users.
