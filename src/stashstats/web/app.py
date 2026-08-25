"""Dash application factory for StashStats."""

from pathlib import Path
from typing import Any

import dash
import dash_bootstrap_components as dbc

from stashstats.client import RavelryClient
from stashstats.web.callbacks.analytics import register_analytics_callbacks
from stashstats.web.callbacks.modal import register_modal_callbacks
from stashstats.web.callbacks.search import register_search_callbacks
from stashstats.web.callbacks.stash import register_stash_callbacks
from stashstats.web.layouts.main import create_main_layout

# Resolve default absolute project assets directory (<root>/assets)
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ASSETS_FOLDER = str(PROJECT_ROOT / "assets")


def create_app(
    client: RavelryClient | None = None,
    title: str = "StashStats",
    external_stylesheets: list[str] | None = None,
    items: list[Any] | None = None,
    assets_folder: str | None = None,
    **dash_kwargs: Any,
) -> dash.Dash:
    """Create and configure the Dash application instance.

    Args:
        client: Optional authenticated RavelryClient instance.
        title: Title of the web application.
        external_stylesheets: List of external stylesheets (defaults to DARKLY and Bootstrap Icons).
        items: Optional initial list of stash items.
        assets_folder: Optional path to static assets folder (defaults to absolute project root / assets).
        **dash_kwargs: Additional keyword arguments passed directly to `dash.Dash`.

    Returns:
        Configured dash.Dash instance with server exposed and root layout.
    """
    if external_stylesheets is None:
        external_stylesheets = [
            dbc.themes.DARKLY,
            dbc.icons.BOOTSTRAP,
        ]

    suppress_callback_exceptions = dash_kwargs.pop("suppress_callback_exceptions", True)
    resolved_assets_folder = assets_folder or dash_kwargs.pop("assets_folder", DEFAULT_ASSETS_FOLDER)

    app = dash.Dash(
        __name__,
        title=title,
        assets_folder=resolved_assets_folder,
        external_stylesheets=external_stylesheets,
        suppress_callback_exceptions=suppress_callback_exceptions,
        **dash_kwargs,
    )

    # Attach client reference for component access
    app.client = client  # type: ignore[attr-defined]

    # Resolve username and initial items if client is available
    username = getattr(client, "_cached_username", None) if client is not None else None
    resolved_items = items
    if resolved_items is None and client is not None:
        try:
            stash_resp = client.get_my_stash()
            resolved_items = stash_resp.stash
        except Exception:
            resolved_items = []

    # Initialize root layout container
    app.layout = create_main_layout(username=username, items=resolved_items)

    # Register reactive callbacks
    register_stash_callbacks(app)
    register_modal_callbacks(app)
    register_search_callbacks(app)
    register_analytics_callbacks(app)

    return app
