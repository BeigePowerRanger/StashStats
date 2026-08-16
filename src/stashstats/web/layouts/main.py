"""Main application layout and tab navigation shell for StashStats."""

from typing import Any

import dash_bootstrap_components as dbc
from dash import dcc, html

from stashstats.web.components.header import create_header
from stashstats.web.layouts.search import create_yarn_search_layout
from stashstats.web.layouts.stash import create_stash_layout

TAB_STYLE = {"backgroundColor": "#222", "color": "#fff"}
SELECTED_TAB_STYLE = {"backgroundColor": "#333", "color": "#00bc8c"}


def create_navigation_tabs(active_tab: str = "tab-stash") -> dcc.Tabs:
    """Create the 4 primary navigation tabs.

    Args:
        active_tab: ID/value of the currently active tab.

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
            ),
            dcc.Tab(
                label="Stash Analytics",
                value="tab-analytics",
                id="tab-analytics-nav",
                style=TAB_STYLE,
                selected_style=SELECTED_TAB_STYLE,
            ),
            dcc.Tab(
                label="Projects",
                value="tab-projects",
                id="tab-projects-nav",
                style=TAB_STYLE,
                selected_style=SELECTED_TAB_STYLE,
            ),
            dcc.Tab(
                label="Yarn Search",
                value="tab-search",
                id="tab-search-nav",
                style=TAB_STYLE,
                selected_style=SELECTED_TAB_STYLE,
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
        if active_tab in ("tab-stash", "tab-personal-stash"):
            tab_content = create_stash_layout(
                items=items,
                sync_status=sync_status,
                pending_count=pending_count,
                last_synced=last_synced,
            )
        elif active_tab in ("tab-search", "tab-yarn-search"):
            tab_content = create_yarn_search_layout()
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
