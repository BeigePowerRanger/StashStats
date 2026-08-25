"""Main application layout and tab navigation shell for StashStats."""

from typing import Any

import dash_bootstrap_components as dbc
from dash import dcc, html

from stashstats.web.components.header import create_header
from stashstats.web.layouts.projects import create_projects_layout
from stashstats.web.layouts.search import create_yarn_search_layout
from stashstats.web.layouts.stash import create_stash_layout

TAB_STYLE = {"backgroundColor": "#222", "color": "#fff"}
SELECTED_TAB_STYLE = {"backgroundColor": "#333", "color": "#00bc8c"}


def create_navigation_tabs(
    active_tab: str = "tab-stash",
    items: Any = None,
    sync_status: str = "Synced",
    pending_count: int = 0,
    last_synced: str | None = None,
    user_id: str | int = "default",
    projects: Any = None,
) -> dcc.Tabs:
    """Create the 4 primary navigation tabs with embedded tab content.

    Args:
        active_tab: ID/value of the currently active tab.
        items: Optional initial list of stash items.
        sync_status: Sync state indicator string.
        pending_count: Number of uncommitted local mutations.
        last_synced: Timestamp string for last sync.
        user_id: Current user identifier for projects PDF scoping.
        projects: Optional initial list of project records.

    Returns:
        Configured dcc.Tabs component.
    """
    normalized_tab = active_tab
    if active_tab == "tab-personal-stash":
        normalized_tab = "tab-stash"
    elif active_tab == "tab-stash-analytics":
        normalized_tab = "tab-analytics"
    elif active_tab == "tab-yarn-search":
        normalized_tab = "tab-search"

    stash_layout = create_stash_layout(
        items=items,
        sync_status=sync_status,
        pending_count=pending_count,
        last_synced=last_synced,
    )
    search_layout = create_yarn_search_layout()
    projects_layout = create_projects_layout(projects=projects, user_id=user_id)

    return dcc.Tabs(
        id="main-tabs",
        value=normalized_tab,
        className="main-navigation-tabs mt-2 mb-3",
        style={"overflowX": "auto"},
        children=[
            dcc.Tab(
                label="Personal Stash",
                value="tab-stash",
                id="tab-stash-nav",
                style=TAB_STYLE,
                selected_style=SELECTED_TAB_STYLE,
                children=[
                    html.Div(style={"height": "15px"}),
                    dbc.Container(
                        stash_layout,
                        id="stash-tab-content",
                        fluid=True,
                        className="p-0",
                    ),
                ],
            ),
            dcc.Tab(
                label="Stash Analytics",
                value="tab-analytics",
                id="tab-analytics-nav",
                style=TAB_STYLE,
                selected_style=SELECTED_TAB_STYLE,
                children=[
                    html.Div(style={"height": "15px"}),
                    dbc.Container(
                        dbc.Alert(
                            "Stash Analytics coming soon.",
                            color="info",
                            className="text-center my-4",
                        ),
                        id="analytics-tab-content",
                        fluid=True,
                        className="p-0",
                    ),
                ],
            ),
            dcc.Tab(
                label="Projects",
                value="tab-projects",
                id="tab-projects-nav",
                style=TAB_STYLE,
                selected_style=SELECTED_TAB_STYLE,
                children=[
                    html.Div(style={"height": "15px"}),
                    dbc.Container(
                        projects_layout,
                        id="projects-tab-content",
                        fluid=True,
                        className="p-0",
                    ),
                ],
            ),
            dcc.Tab(
                label="Yarn Search",
                value="tab-search",
                id="tab-search-nav",
                style=TAB_STYLE,
                selected_style=SELECTED_TAB_STYLE,
                children=[
                    html.Div(style={"height": "15px"}),
                    dbc.Container(
                        search_layout,
                        id="search-tab-content",
                        fluid=True,
                        className="p-0",
                    ),
                ],
            ),
        ],
    )


def create_main_layout(
    username: str | None = None,
    active_tab: str = "tab-stash",
    sync_status: str = "Synced",
    pending_count: int = 0,
    last_synced: str | None = None,
    tab_content: Any = None,
    items: Any = None,
    projects: Any = None,
) -> dbc.Container:
    """Create root application layout shell with header and navigation tabs.

    Args:
        username: Authenticated Ravelry username.
        active_tab: Tab ID of active tab.
        sync_status: Sync state indicator string.
        pending_count: Number of uncommitted local mutations.
        last_synced: Timestamp string for last sync.
        tab_content: Optional custom content for the tab container.
        items: Optional initial list of stash items.
        projects: Optional initial list of project items.

    Returns:
        Root dbc.Container component.
    """
    header = create_header(
        username=username,
        sync_status=sync_status,
        pending_count=pending_count,
        last_synced=last_synced,
    )

    tabs = create_navigation_tabs(
        active_tab=active_tab,
        items=items,
        sync_status=sync_status,
        pending_count=pending_count,
        last_synced=last_synced,
        user_id=username or "default",
        projects=projects,
    )

    content_area = html.Div(
        id="tab-content",
        className="tab-content-container p-2",
        children=[tabs] if tab_content is None else tab_content,
    )

    body_container = dbc.Container(
        children=[
            content_area,
        ],
        fluid=False,
        style={"maxWidth": "85%", "width": "85%", "margin": "0 auto"},
        className="px-2 py-2",
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
