"""Dash callbacks for Projects tab: PDF upload, list, delete, and inline viewer."""

import base64
import logging
from pathlib import Path
from typing import Any

import dash
from dash import Input, Output, State, ctx

from stashstats.storage import (
    DEFAULT_DATA_DIR,
    delete_project_pdf,
    list_project_pdfs,
    save_project_pdf,
)

logger = logging.getLogger("stashstats.web.projects")

MAX_PDF_BYTES = 25 * 1024 * 1024  # 25 MB


def _decode_upload(contents: str) -> tuple[str, bytes] | tuple[None, None]:
    """Decode a dcc.Upload base64 payload into (mime_type, bytes).

    Args:
        contents: Raw dcc.Upload contents string (``data:<mime>;base64,<data>``).

    Returns:
        Tuple of (mime_type, raw_bytes) or (None, None) on error.
    """
    try:
        header, b64_data = contents.split(",", 1)
        mime = header.split(":")[1].split(";")[0]
        return mime, base64.b64decode(b64_data)
    except Exception:
        return None, None


def register_projects_callbacks(app: dash.Dash) -> None:
    """Register reactive Dash callbacks for Projects tab PDF management.

    Args:
        app: dash.Dash application instance.
    """
    if getattr(app, "_projects_callbacks_registered", False):
        return
    app._projects_callbacks_registered = True  # type: ignore[attr-defined]

    @app.callback(
        Output({"type": "project-pdf-list", "index": dash.ALL}, "children"),
        Output({"type": "project-pdf-error", "index": dash.ALL}, "children"),
        Input({"type": "project-pdf-upload", "index": dash.ALL}, "contents"),
        State({"type": "project-pdf-upload", "index": dash.ALL}, "filename"),
        State({"type": "project-pdf-upload", "index": dash.ALL}, "id"),
        State("projects-user-store", "data"),
        prevent_initial_call=True,
    )
    def handle_pdf_upload(
        contents_list: list[str | None],
        filenames_list: list[str | None],
        ids_list: list[dict],
        user_data: dict | None,
    ) -> tuple[list[Any], list[Any]]:
        """Handle PDF upload for a project: validate, save, refresh file list.

        Args:
            contents_list: Base64 upload payloads from dcc.Upload per project.
            filenames_list: Original filenames per project.
            ids_list: Component IDs (contain project_id index) per project.
            user_data: Store dict with ``user_id`` key.

        Returns:
            Tuple of (file_list_children, error_children) per project.
        """
        from stashstats.web.components.projects import create_pdf_file_list  # noqa: PLC0415

        user_id = (user_data or {}).get("user_id", "default")
        base_dir = DEFAULT_DATA_DIR

        list_outputs: list[Any] = []
        error_outputs: list[Any] = []

        for contents, filename, comp_id in zip(contents_list, filenames_list, ids_list):
            project_id = str(comp_id.get("index", "unknown"))

            if not contents or not filename:
                # No upload triggered for this slot — refresh list only
                pdfs = list_project_pdfs(user_id, project_id, base_dir=base_dir)
                list_outputs.append(create_pdf_file_list(pdfs, project_id, user_id))
                error_outputs.append("")
                continue

            mime, raw = _decode_upload(contents)
            if mime != "application/pdf":
                pdfs = list_project_pdfs(user_id, project_id, base_dir=base_dir)
                list_outputs.append(create_pdf_file_list(pdfs, project_id, user_id))
                error_outputs.append("Only PDF files are accepted.")
                continue

            if raw is not None and len(raw) > MAX_PDF_BYTES:
                pdfs = list_project_pdfs(user_id, project_id, base_dir=base_dir)
                list_outputs.append(create_pdf_file_list(pdfs, project_id, user_id))
                error_outputs.append("File exceeds 25 MB limit.")
                continue

            if raw is not None:
                save_project_pdf(user_id, project_id, filename, raw, base_dir=base_dir)
                logger.info(f"PDF saved: user={user_id} project={project_id} file={filename}")

            pdfs = list_project_pdfs(user_id, project_id, base_dir=base_dir)
            list_outputs.append(create_pdf_file_list(pdfs, project_id, user_id))
            error_outputs.append("")

        return list_outputs, error_outputs

    @app.callback(
        Output({"type": "project-pdf-list", "index": dash.MATCH}, "children", allow_duplicate=True),
        Input({"type": "project-pdf-delete-btn", "index": dash.MATCH, "filename": dash.ALL}, "n_clicks"),
        State({"type": "project-pdf-delete-btn", "index": dash.MATCH, "filename": dash.ALL}, "id"),
        State("projects-user-store", "data"),
        prevent_initial_call=True,
    )
    def handle_pdf_delete(
        n_clicks_list: list[int | None],
        ids_list: list[dict],
        user_data: dict | None,
    ) -> Any:
        """Delete a PDF for a project when its delete button is clicked.

        Args:
            n_clicks_list: Click counts from delete buttons.
            ids_list: Component IDs with ``index`` (project_id) and ``filename``.
            user_data: Store dict with ``user_id`` key.

        Returns:
            Updated file list component children for the project.
        """
        from stashstats.web.components.projects import create_pdf_file_list  # noqa: PLC0415

        if not any(n_clicks_list):
            raise dash.exceptions.PreventUpdate

        triggered = ctx.triggered_id
        if not triggered or not isinstance(triggered, dict):
            raise dash.exceptions.PreventUpdate

        user_id = (user_data or {}).get("user_id", "default")
        project_id = str(triggered.get("index", "unknown"))
        filename = triggered.get("filename", "")

        delete_project_pdf(user_id, project_id, filename, base_dir=DEFAULT_DATA_DIR)
        logger.info(f"PDF deleted: user={user_id} project={project_id} file={filename}")

        pdfs = list_project_pdfs(user_id, project_id, base_dir=DEFAULT_DATA_DIR)
        return create_pdf_file_list(pdfs, project_id, user_id)

    @app.callback(
        Output({"type": "project-pdf-viewer", "index": dash.MATCH}, "src"),
        Input({"type": "project-pdf-view-btn", "index": dash.MATCH, "filename": dash.ALL}, "n_clicks"),
        State({"type": "project-pdf-view-btn", "index": dash.MATCH, "filename": dash.ALL}, "id"),
        State("projects-user-store", "data"),
        prevent_initial_call=True,
    )
    def handle_pdf_view(
        n_clicks_list: list[int | None],
        ids_list: list[dict],
        user_data: dict | None,
    ) -> str:
        """Set iframe src to serve-route URL when a filename is clicked.

        Args:
            n_clicks_list: Click counts from view buttons.
            ids_list: Component IDs with ``index`` (project_id) and ``filename``.
            user_data: Store dict with ``user_id`` key.

        Returns:
            URL string for the PDF serve route.
        """
        if not any(n_clicks_list):
            raise dash.exceptions.PreventUpdate

        triggered = ctx.triggered_id
        if not triggered or not isinstance(triggered, dict):
            raise dash.exceptions.PreventUpdate

        user_id = (user_data or {}).get("user_id", "default")
        project_id = str(triggered.get("index", "unknown"))
        filename = triggered.get("filename", "")

        return f"/projects/pdf/{user_id}/{project_id}/{filename}"
