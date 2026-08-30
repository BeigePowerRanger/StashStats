"""Dash application factory for StashStats."""

from pathlib import Path
from typing import Any

import dash
import dash_bootstrap_components as dbc
from flask import Response, abort

from stashstats.client import RavelryClient
from stashstats.web.callbacks.analytics import register_analytics_callbacks
from stashstats.web.callbacks.manual_yarn import register_manual_yarn_callbacks
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

    from stashstats.auth import account_manager  # noqa: PLC0415

    # Attach client reference for component access
    active_client = client if client is not None else account_manager.get_client()
    app.client = active_client  # type: ignore[attr-defined]

    # Resolve username and initial items/projects if client is available
    active_label = account_manager.get_active_label()
    username = getattr(active_client, "_cached_username", None) if active_client is not None else None
    resolved_items = items
    resolved_projects = None
    if active_client is not None:
        if username is None:
            try:
                username = active_client.username
            except Exception:
                username = None

        if resolved_items is None:
            try:
                if hasattr(active_client, "get_all_my_stash"):
                    resolved_items = active_client.get_all_my_stash()
                else:
                    stash_resp = active_client.get_my_stash()
                    resolved_items = stash_resp.stash
            except Exception:
                resolved_items = []
        try:
            proj_resp = active_client.get_my_projects()
            resolved_projects = proj_resp.projects
        except Exception:
            resolved_projects = []

    # Initialize root layout container
    app.layout = create_main_layout(
        username=username,
        items=resolved_items,
        projects=resolved_projects,
        active_label=active_label,
    )

    # Register reactive callbacks
    register_stash_callbacks(app)
    register_modal_callbacks(app)
    register_manual_yarn_callbacks(app)
    register_search_callbacks(app)
    register_analytics_callbacks(app)

    # Register Projects tab callbacks
    from stashstats.web.callbacks.projects import register_projects_callbacks  # noqa: PLC0415
    register_projects_callbacks(app)

    # ---------------------------------------------------------------------------
    # PDF serve route: GET /projects/pdf/<user_id>/<project_id>/<filename>
    # ---------------------------------------------------------------------------
    @app.server.route("/projects/pdf/<user_id>/<project_id>/<path:filename>")
    def serve_project_pdf(user_id: str, project_id: str, filename: str):
        """Stream a stored project PDF to the browser.

        Args:
            user_id: Authenticated user identifier (path segment).
            project_id: Project identifier (path segment).
            filename: PDF filename to serve (path segment).

        Returns:
            Flask response with Content-Type application/pdf, or 404/400 on error.
        """
        if not user_id or not project_id or not filename:
            abort(400)
        if "/" in filename or "\\" in filename or ".." in filename or "\x00" in filename:
            abort(400)

        from stashstats.storage import get_project_pdf_bytes  # noqa: PLC0415

        pdf_bytes = get_project_pdf_bytes(user_id, project_id, filename)
        if pdf_bytes is None:
            abort(404)

        return Response(pdf_bytes, mimetype="application/pdf")

    return app
