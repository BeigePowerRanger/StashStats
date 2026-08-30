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
    sync_status: str = "Synced",
    last_synced: str | None = None,
    include_stores: bool = True,
) -> dbc.Container:
    """Create the Projects tab content layout.

    Renders a sync control bar and a card grid of project entries, each with
    an optional PDF upload zone and inline viewer. When no projects are loaded,
    shows a placeholder alert.

    Args:
        projects: Optional list of project dicts fetched from Ravelry.
        user_id: Current user identifier for scoping PDF storage.
        sync_status: Initial sync status string.
        last_synced: Timestamp string for last sync.

    Returns:
        Configured dbc.Container layout.
    """
    raw_projects: list[dict[str, Any]] = []
    if projects:
        for p in projects:
            if hasattr(p, "model_dump"):
                raw_projects.append(p.model_dump())
            elif isinstance(p, dict):
                raw_projects.append(p)

    stores: list[Any] = []
    if include_stores:
        stores = [
            dcc.Store(id="projects-user-store", data={"user_id": str(user_id)}),
            dcc.Store(id="projects-raw-store", data=raw_projects),
        ]

    sync_btn = dbc.Button(
        [html.I(className="bi bi-arrow-repeat me-1"), "Sync Now"],
        id="projects-sync-btn",
        color="success",
        size="sm",
        className="fw-semibold me-2 d-flex align-items-center",
    )

    sync_badge = dbc.Badge(
        sync_status,
        color="success",
        pill=True,
        className="me-2 px-2 py-1 align-self-center",
        id="projects-sync-badge",
    )

    last_synced_text = f"Last synced: {last_synced}" if last_synced else "Last synced: Never"
    last_synced_elem = html.Small(
        last_synced_text,
        className="text-muted align-self-center",
        id="projects-last-synced",
    )

    sync_row = dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        sync_btn,
                        sync_badge,
                        last_synced_elem,
                    ],
                    className="d-flex align-items-center mb-3",
                ),
                xs=12,
            )
        ]
    )

    if not raw_projects:
        cards_content = dbc.Alert(
            [
                html.I(className="bi bi-folder2-open me-2"),
                "No projects loaded. Sync with Ravelry to see your projects.",
            ],
            color="info",
            className="text-center my-4",
            id="projects-empty-alert",
        )
    else:
        cards_content = html.Div(
            [create_project_card(project, user_id=user_id) for project in raw_projects]
        )

    cards_container = html.Div(
        cards_content,
        id="projects-cards-container",
    )

    return dbc.Container(
        [*stores, sync_row, cards_container],
        fluid=True,
        className="p-0",
    )
