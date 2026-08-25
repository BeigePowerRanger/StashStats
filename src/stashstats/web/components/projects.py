"""UI component factories for the Projects tab PDF management UI."""

from typing import Any

import dash_bootstrap_components as dbc
from dash import dcc, html


def create_pdf_file_list(
    filenames: list[str],
    project_id: str | int,
    user_id: str | int,
) -> list[Any]:
    """Render the list of attached PDFs for a project.

    Each file entry shows a clickable filename button (opens inline viewer) and
    a delete button. Returns an empty-state message when no files exist.

    Args:
        filenames: Sorted list of PDF filenames attached to the project.
        project_id: Project identifier used to scope button IDs.
        user_id: User identifier (not used in ID but kept for future use).

    Returns:
        List of Dash component children suitable for a ``children`` prop.
    """
    if not filenames:
        return [html.P("No PDFs attached.", className="text-muted small mb-0")]

    rows: list[Any] = []
    for fname in filenames:
        row = dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        fname,
                        id={"type": "project-pdf-view-btn", "index": str(project_id), "filename": fname},
                        color="link",
                        size="sm",
                        className="text-start p-0",
                        n_clicks=0,
                    ),
                    width="auto",
                    className="me-auto",
                ),
                dbc.Col(
                    dbc.Button(
                        html.I(className="bi bi-trash"),
                        id={"type": "project-pdf-delete-btn", "index": str(project_id), "filename": fname},
                        color="danger",
                        size="sm",
                        outline=True,
                        n_clicks=0,
                        title=f"Delete {fname}",
                    ),
                    width="auto",
                ),
            ],
            className="align-items-center mb-1 g-1",
        )
        rows.append(row)
    return rows


def create_pdf_viewer(src_url: str = "") -> html.Iframe:
    """Render an inline PDF viewer iframe.

    Args:
        src_url: Initial src URL for the iframe (empty string = blank).

    Returns:
        ``html.Iframe`` configured for PDF display.
    """
    return html.Iframe(
        src=src_url,
        style={
            "width": "100%",
            "height": "600px",
            "border": "1px solid #444",
            "borderRadius": "4px",
            "backgroundColor": "#1a1a1a",
        },
    )


def create_pdf_upload_zone(project_id: str | int) -> dcc.Upload:
    """Render the dcc.Upload dropzone for a project.

    Accepts only PDF files; multiple uploads allowed.

    Args:
        project_id: Project identifier used to scope the component ID.

    Returns:
        Configured ``dcc.Upload`` component.
    """
    return dcc.Upload(
        id={"type": "project-pdf-upload", "index": str(project_id)},
        accept=".pdf,application/pdf",
        multiple=False,  # one at a time; re-trigger for each file
        children=html.Div(
            [
                html.I(className="bi bi-file-earmark-pdf me-2"),
                "Drag & drop a PDF or ",
                html.A("click to upload", href="#"),
            ],
            className="text-center text-muted py-2 small",
        ),
        style={
            "border": "2px dashed #555",
            "borderRadius": "6px",
            "padding": "8px",
            "cursor": "pointer",
        },
    )
