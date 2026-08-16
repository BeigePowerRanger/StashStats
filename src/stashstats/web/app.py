"""Dash application factory for StashStats."""

from typing import Any

import dash
import dash_bootstrap_components as dbc

from stashstats.client import RavelryClient
from stashstats.web.callbacks.modal import register_modal_callbacks
from stashstats.web.callbacks.search import register_search_callbacks
from stashstats.web.callbacks.stash import register_stash_callbacks
from stashstats.web.layouts.main import create_main_layout


def create_app(
    client: RavelryClient | None = None,
    title: str = "StashStats",
    external_stylesheets: list[str] | None = None,
    items: list[Any] | None = None,
    **dash_kwargs: Any,
) -> dash.Dash:
    """Create and configure the Dash application instance.

    Args:
        client: Optional authenticated RavelryClient instance.
        title: Title of the web application.
        external_stylesheets: List of external stylesheets (defaults to DARKLY and Bootstrap Icons).
        items: Optional initial list of stash items.
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

    app = dash.Dash(
        __name__,
        title=title,
        external_stylesheets=external_stylesheets,
        suppress_callback_exceptions=suppress_callback_exceptions,
        **dash_kwargs,
    )

    # Attach client reference for component access
    app.client = client  # type: ignore[attr-defined]

    # Resolve username if cached on client
    username = getattr(client, "_cached_username", None) if client is not None else None

    # Initialize root layout container
    app.layout = create_main_layout(username=username, items=items)

    # Register reactive callbacks
    register_stash_callbacks(app)
    register_modal_callbacks(app)
    register_search_callbacks(app)

    return app

