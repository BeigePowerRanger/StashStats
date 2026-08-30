"""Tests for header component and main layout in stashstats.web."""

from typing import Any

from dash import dcc
from dash.development.base_component import Component

from stashstats.web.app import create_app
from stashstats.web.components.header import create_header
from stashstats.web.layouts.main import create_main_layout


def find_component_by_id(tree: Any, component_id: str) -> Component | None:
    """Recursively find a Dash component by its id."""
    if not isinstance(tree, Component) and not hasattr(tree, "to_plotly_json"):
        if isinstance(tree, list):
            for child in tree:
                res = find_component_by_id(child, component_id)
                if res is not None:
                    return res
        return None

    if getattr(tree, "id", None) == component_id:
        return tree

    children = getattr(tree, "children", None)
    if children is not None:
        if isinstance(children, list):
            for child in children:
                res = find_component_by_id(child, component_id)
                if res is not None:
                    return res
        else:
            return find_component_by_id(children, component_id)

    return None


def test_header_branding() -> None:
    """Verify header component contains StashStats branding and logo."""
    header = create_header()
    brand = find_component_by_id(header, "header-brand")
    assert brand is not None
    logo = find_component_by_id(header, "header-logo")
    assert logo is not None
    json_repr = str(logo.to_plotly_json())
    assert "/assets/Images/logo_color.png" in json_repr


def test_header_user_badge_default() -> None:
    """Verify header displays default guest/offline badge with DEV env pill."""
    header = create_header()
    badge = find_component_by_id(header, "header-user-badge")
    assert badge is not None
    assert "@Guest" in str(badge.to_plotly_json()) or "@Offline" in str(badge.to_plotly_json())
    env_pill = find_component_by_id(header, "header-env-pill")
    assert env_pill is not None
    assert "DEV" in str(env_pill.to_plotly_json())


def test_header_user_badge_authenticated_and_env_pill() -> None:
    """Verify header displays @username badge, PROD pill, and greeting."""
    header = create_header(username="Thotsky", active_label="prod")
    badge = find_component_by_id(header, "header-user-badge")
    assert badge is not None
    assert "@Thotsky" in str(badge.to_plotly_json())

    env_pill = find_component_by_id(header, "header-env-pill")
    assert env_pill is not None
    assert "PROD" in str(env_pill.to_plotly_json())

    greeting = find_component_by_id(header, "header-greeting")
    assert greeting is not None
    assert "Hello Thotsky!" in str(greeting.to_plotly_json())


def test_header_sync_indicator_clean() -> None:
    """Verify sync indicator displays Synced status and timestamp."""
    header = create_header(sync_status="Synced", pending_count=0, last_synced="Today 14:32")
    badge = find_component_by_id(header, "header-sync-badge")
    assert badge is not None
    assert "Synced" in str(badge.to_plotly_json())

    timestamp = find_component_by_id(header, "header-last-synced")
    assert timestamp is not None
    assert "Today 14:32" in str(timestamp.to_plotly_json())


def test_header_sync_indicator_pending() -> None:
    """Verify sync indicator displays pending mutations count."""
    header = create_header(pending_count=3)
    badge = find_component_by_id(header, "header-sync-badge")
    assert badge is not None
    assert "3 pending" in str(badge.to_plotly_json())
    assert getattr(badge, "color", None) == "warning"


def test_main_layout_tabs_structure() -> None:
    """Verify main layout contains the 4 required navigation tabs and content area."""
    layout = create_main_layout()
    tabs = find_component_by_id(layout, "main-tabs")
    assert tabs is not None
    assert isinstance(tabs, dcc.Tabs)
    assert getattr(tabs, "value", None) == "tab-stash"

    # Verify tab children
    tab_values = [getattr(tab, "value", None) for tab in tabs.children if isinstance(tab, dcc.Tab)]
    expected_tab_values = [
        "tab-stash",
        "tab-analytics",
        "tab-projects",
        "tab-search",
    ]
    assert tab_values == expected_tab_values

    # Verify tab styling
    for tab in tabs.children:
        if isinstance(tab, dcc.Tab):
            assert tab.style == {"backgroundColor": "#222", "color": "#fff"}
            assert tab.selected_style == {"backgroundColor": "#333", "color": "#00bc8c"}

    # Verify tab content container exists
    tab_content = find_component_by_id(layout, "tab-content")
    assert tab_content is not None

    # Verify embedded tab content containers
    assert find_component_by_id(layout, "stash-tab-content") is not None
    assert find_component_by_id(layout, "analytics-tab-content") is not None
    assert find_component_by_id(layout, "projects-tab-content") is not None
    assert find_component_by_id(layout, "search-tab-content") is not None


def test_main_layout_with_username() -> None:
    """Verify main layout passes username to header."""
    layout = create_main_layout(username="Thotsky")
    badge = find_component_by_id(layout, "header-user-badge")
    assert badge is not None
    assert "@Thotsky" in str(badge.to_plotly_json())
    greeting = find_component_by_id(layout, "header-greeting")
    assert greeting is not None
    assert "Hello Thotsky!" in str(greeting.to_plotly_json())


def test_app_integration_with_main_layout() -> None:
    """Verify create_app integrates main layout with header and tabs."""
    app = create_app()
    assert app.layout is not None
    assert getattr(app.layout, "id", None) == "app-root"

    tabs = find_component_by_id(app.layout, "main-tabs")
    assert tabs is not None

    brand = find_component_by_id(app.layout, "header-brand")
    assert brand is not None
