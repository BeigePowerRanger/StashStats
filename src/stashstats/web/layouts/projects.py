"""Projects tab layout with optional PDF attachment per project."""

from typing import Any

import dash_bootstrap_components as dbc
from dash import dcc, html

from stashstats.web.components.projects import (
    create_pdf_file_list,
    create_pdf_upload_zone,
    create_pdf_viewer,
)


def create_project_card(
    project: dict[str, Any],
    user_id: str | int = "default",
    existing_pdfs: list[str] | None = None,
) -> dbc.Card:
    """Render a single project entry card with PDF upload zone and viewer.

    Args:
        project: Dict of project data (expects at minimum 'id' and 'name').
        user_id: Current user identifier for scoping PDF storage.
        existing_pdfs: Pre-loaded list of PDF filenames for this project.

    Returns:
        Configured dbc.Card component.
    """
    project_id = str(project.get("id", "unknown"))
    name = project.get("name") or project.get("pattern_name") or "Untitled Project"
    status = project.get("status_name") or ""
    progress = project.get("progress") or 0

    pdfs = existing_pdfs or []

    return dbc.Card(
        [
            dbc.CardHeader(
                dbc.Row(
                    [
                        dbc.Col(html.Strong(name), width=True),
                        dbc.Col(
                            dbc.Badge(status, color="secondary", className="ms-2") if status else "",
                            width="auto",
                        ),
                    ],
                    className="align-items-center g-1",
                ),
                className="py-2",
            ),
            dbc.CardBody(
                [
                    # Progress bar (non-zero progress only)
                    (
                        dbc.Progress(
                            value=progress,
                            label=f"{progress}%",
                            className="mb-3",
                            style={"height": "8px"},
                        )
                        if progress
                        else html.Div()
                    ),
                    # PDF section
                    html.Hr(className="my-2"),
                    html.P("Attached PDFs", className="small fw-semibold mb-1"),
                    create_pdf_upload_zone(project_id),
                    html.Div(
                        id={"type": "project-pdf-error", "index": project_id},
                        className="text-danger small mt-1",
                        children="",
                    ),
                    html.Div(
                        id={"type": "project-pdf-list", "index": project_id},
                        className="mt-2",
                        children=create_pdf_file_list(pdfs, project_id, user_id),
                    ),
                    # Inline viewer — initially hidden (empty src)
                    html.Div(
                        html.Iframe(
                            id={"type": "project-pdf-viewer", "index": project_id},
                            src="",
                            style={
                                "width": "100%",
                                "height": "600px",
                                "border": "1px solid #444",
                                "borderRadius": "4px",
                                "backgroundColor": "#1a1a1a",
                                "display": "none",
                            },
                        ),
                        id={"type": "project-pdf-viewer-container", "index": project_id},
                        className="mt-2",
                    ),
                ],
                className="pb-2",
            ),
        ],
        className="mb-3 bg-dark text-light border-secondary",
    )


def create_projects_layout(
    projects: list[dict[str, Any]] | None = None,
    user_id: str | int = "default",
) -> dbc.Container:
    """Create the Projects tab content layout.

    Renders a card grid of project entries, each with an optional PDF upload
    zone and inline viewer. When no projects are loaded, shows a placeholder.

    Args:
        projects: Optional list of project dicts fetched from Ravelry.
        user_id: Current user identifier for scoping PDF storage.

    Returns:
        Configured dbc.Container layout.
    """
    # dcc.Store holds user_id for callbacks that cannot access it otherwise
    user_store = dcc.Store(id="projects-user-store", data={"user_id": str(user_id)})

    if not projects:
        return dbc.Container(
            [
                user_store,
                dbc.Alert(
                    [
                        html.I(className="bi bi-folder2-open me-2"),
                        "No projects loaded. Sync with Ravelry to see your projects.",
                    ],
                    color="info",
                    className="text-center my-4",
                    id="projects-empty-alert",
                ),
            ],
            fluid=True,
            className="p-0",
        )

    cards = [
        create_project_card(project, user_id=user_id)
        for project in projects
    ]

    return dbc.Container(
        [user_store, *cards],
        fluid=True,
        className="p-0",
    )
