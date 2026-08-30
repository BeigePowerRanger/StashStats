"""Projects tab layout with accordion view and search/sort/pagination."""

from typing import Any

import dash_bootstrap_components as dbc
from dash import dcc, html

from stashstats.web.components.projects import (
    create_grouped_projects_accordion,
)


def create_projects_layout(
    projects: list[dict[str, Any]] | None = None,
    user_id: str | int = "default",
    sync_status: str = "Synced",
    last_synced: str | None = None,
    include_stores: bool = True,
) -> dbc.Container:
    """Create the Projects tab content layout.

    Renders a sync control bar, search/sort controls, and an accordion of projects.

    Args:
        projects: Optional list of project dicts fetched from Ravelry.
        user_id: Current user identifier for scoping PDF storage.
        sync_status: Initial sync status string.
        last_synced: Timestamp string for last sync.
        include_stores: Whether to include the dcc.Store components in the layout.

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

    # Controls Row
    controls_row = dbc.Row(
        [
            dbc.Col(
                dbc.Input(
                    id="projects-search-input",
                    placeholder="Search projects...",
                    type="text",
                    debounce=True,
                ),
                md=8,
                className="mb-2 mb-md-0",
            ),
            dbc.Col(
                dbc.Select(
                    id="projects-sort-dropdown",
                    options=[
                        {"label": "Date (Newest First)", "value": "date_desc"},
                        {"label": "Name (A-Z)", "value": "name_asc"},
                        {"label": "Progress (Highest First)", "value": "progress_desc"},
                        {"label": "Status", "value": "status_asc"},
                    ],
                    value="date_desc",
                ),
                md=4,
            ),
        ],
        className="mb-3",
    )

    # Main container for the accordion
    # Initially we pass the raw projects, but the callback will manage filtering/pagination
    accordion_container = html.Div(
        create_grouped_projects_accordion(raw_projects[:10] if raw_projects else []),
        id="projects-accordion-container",
    )
    
    # Pagination
    pagination_row = dbc.Row(
        [
            dbc.Col(
                dbc.Pagination(
                    id="projects-pagination",
                    active_page=1,
                    max_value=max(1, (len(raw_projects) + 9) // 10) if raw_projects else 1,
                    fully_expanded=False,
                    first_last=True,
                    previous_next=True,
                    className="mt-3 justify-content-center",
                ),
            )
        ]
    )

    return dbc.Container(
        [*stores, sync_row, controls_row, accordion_container, pagination_row],
        fluid=True,
        className="p-0",
    )
