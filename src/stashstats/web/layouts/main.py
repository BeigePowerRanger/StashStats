"""Main application layout and tab navigation shell for StashStats."""

from typing import Any

import dash_bootstrap_components as dbc
from dash import html

from stashstats.web.components.header import create_header
from stashstats.web.layouts.stash import create_stash_layout


def create_navigation_tabs(active_tab: str = "tab-personal-stash") -> dbc.Tabs:
    """Create the 4 primary navigation tabs.

    Args:
        active_tab: ID of the currently active tab.

    Returns:
        Configured dbc.Tabs component.
    """
    return dbc.Tabs(
        id="main-tabs",
        active_tab=active_tab,
        className="nav-tabs mt-2 mb-3 border-bottom border-secondary",
        children=[
            dbc.Tab(
                label="Personal Stash",
                tab_id="tab-personal-stash",
                id="tab-personal-stash-nav",
                label_class_name="fw-semibold text-light",
                active_label_class_name="fw-bold text-success border-bottom border-success border-2",
            ),
            dbc.Tab(
                label="Stash Analytics",
                tab_id="tab-stash-analytics",
                id="tab-stash-analytics-nav",
                label_class_name="fw-semibold text-light",
                active_label_class_name="fw-bold text-success border-bottom border-success border-2",
            ),
            dbc.Tab(
                label="Projects",
                tab_id="tab-projects",
                id="tab-projects-nav",
                label_class_name="fw-semibold text-light",
                active_label_class_name="fw-bold text-success border-bottom border-success border-2",
            ),
            dbc.Tab(
                label="Yarn Search",
                tab_id="tab-yarn-search",
                id="tab-yarn-search-nav",
                label_class_name="fw-semibold text-light",
                active_label_class_name="fw-bold text-success border-bottom border-success border-2",
            ),
        ],
    )


def create_main_layout(
    username: str | None = None,
    active_tab: str = "tab-personal-stash",
    sync_status: str = "Synced",
    pending_count: int = 0,
    last_synced: str | None = None,
    tab_content: Any = None,
    items: Any = None,
) -> dbc.Container:
    """Create root application layout shell with header and navigation tabs.

    Args:
        username: Authenticated Ravelry username.
        active_tab: Tab ID of active tab.
        sync_status: Sync state indicator string.
        pending_count: Number of uncommitted local mutations.
        last_synced: Timestamp string for last sync.
        tab_content: Initial content for the active tab content container.
        items: Optional initial list of stash items.

    Returns:
        Root dbc.Container component.
    """
    header = create_header(
        username=username,
        sync_status=sync_status,
        pending_count=pending_count,
        last_synced=last_synced,
    )

    tabs = create_navigation_tabs(active_tab=active_tab)

    if tab_content is None:
        if active_tab == "tab-personal-stash":
            tab_content = create_stash_layout(
                items=items,
                sync_status=sync_status,
                pending_count=pending_count,
                last_synced=last_synced,
            )
        else:
            tab_content = []

    content_area = html.Div(
        id="tab-content",
        className="tab-content-container p-2",
        children=tab_content,
    )

    body_container = dbc.Container(
        children=[
            tabs,
            content_area,
        ],
        fluid=True,
        className="px-4 py-2",
    )

    return dbc.Container(
        id="app-root",
        fluid=True,
        className="p-0 bg-dark text-light min-vh-100",
        children=[
            header,
            body_container,
        ],
    )
