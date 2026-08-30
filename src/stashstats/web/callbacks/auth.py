"""Reactive Dash callbacks for account switching and authentication state management."""

import logging
from typing import Any

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, ctx, html

from stashstats.auth import account_manager

logger = logging.getLogger("stashstats.web.auth")


def handle_account_modal_toggle_logic(
    badge_clicks: int | None,
    cancel_clicks: int | None,
    is_open: bool,
    account_mgr: Any = None,
    triggered_id: str | None = None,
) -> tuple[bool, Any, Any, str]:
    """Toggle account switch confirmation modal state and content."""
    if not badge_clicks and not cancel_clicks and not triggered_id:
        raise dash.exceptions.PreventUpdate

    mgr = account_mgr or account_manager
    target_label = mgr.get_target_label().upper()

    if triggered_id == "account-switch-cancel-btn":
        return False, dash.no_update, dash.no_update, dash.no_update

    body_content = [
        html.P(
            f"Switch active session to {target_label} account?",
            className="fw-semibold fs-5 mb-2",
        ),
        html.P(
            "All currently loaded stash items, projects, and analytics data will reload with the new account credentials.",
            className="text-muted small mb-0",
        ),
    ]
    btn_children = [
        html.I(className="bi bi-check-circle me-1"),
        f"Switch to {target_label}",
    ]
    btn_color = "warning" if target_label == "DEV" else "danger"

    return True, body_content, btn_children, btn_color


def handle_account_switch_confirm_logic(
    n_clicks: int | None,
    account_mgr: Any = None,
) -> tuple[bool, list[Any], str, dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], dict[str, str]]:
    """Execute account switch: toggle active credentials, reload stash + projects, update header badge."""
    if not n_clicks:
        raise dash.exceptions.PreventUpdate

    mgr = account_mgr or account_manager
    new_label, username = mgr.switch()
    client = mgr.get_client()

    fresh_stash: list[dict[str, Any]] = []
    try:
        if hasattr(client, "get_all_my_stash"):
            raw_stash = client.get_all_my_stash()
        else:
            raw_stash = client.get_my_stash().stash
        fresh_stash = [
            it.model_dump() if hasattr(it, "model_dump") else it
            for it in raw_stash
        ]
    except Exception as e:
        logger.warning(f"Failed to fetch stash on account switch: {e}")

    fresh_projects: list[dict[str, Any]] = []
    try:
        raw_projects = client.get_my_projects().projects
        fresh_projects = [
            it.model_dump() if hasattr(it, "model_dump") else it
            for it in raw_projects
        ]
    except Exception as e:
        logger.warning(f"Failed to fetch projects on account switch: {e}")

    env_label = new_label.upper()
    env_color = "warning" if env_label == "DEV" else "danger"
    env_pill = dbc.Badge(
        env_label,
        color=env_color,
        pill=True,
        className="ms-1 px-2 py-0 fs-7",
        id="header-env-pill",
    )
    user_label = f"@{username}" if username else "@Guest"
    badge_children = [
        html.Span(user_label, className="me-1 fw-bold"),
        env_pill,
    ]

    greeting_text = f"Hello {username}!" if username else ""
    greeting_style = {} if username else {"display": "none"}
    user_store_data = {"user_id": str(username or "default")}

    return (
        False,
        badge_children,
        greeting_text,
        greeting_style,
        fresh_stash,
        fresh_projects,
        user_store_data,
    )


def register_auth_callbacks(app: dash.Dash) -> None:
    """Register callbacks for account modal and switching."""
    if getattr(app, "_auth_callbacks_registered", False):
        return
    app._auth_callbacks_registered = True  # type: ignore[attr-defined]

    @app.callback(
        Output("account-switch-modal", "is_open"),
        Output("account-switch-modal-body", "children"),
        Output("account-switch-confirm-btn", "children"),
        Output("account-switch-confirm-btn", "color"),
        Input("header-user-badge", "n_clicks"),
        Input("account-switch-cancel-btn", "n_clicks"),
        State("account-switch-modal", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_account_modal(
        badge_clicks: int | None,
        cancel_clicks: int | None,
        is_open: bool,
    ) -> tuple[bool, Any, Any, str]:
        triggered = ctx.triggered_id if ctx else None
        return handle_account_modal_toggle_logic(
            badge_clicks=badge_clicks,
            cancel_clicks=cancel_clicks,
            is_open=is_open,
            triggered_id=triggered,
        )

    @app.callback(
        Output("account-switch-modal", "is_open", allow_duplicate=True),
        Output("header-user-badge", "children"),
        Output("header-greeting", "children"),
        Output("header-greeting", "style"),
        Output("stash-raw-store", "data", allow_duplicate=True),
        Output("projects-raw-store", "data", allow_duplicate=True),
        Output("projects-user-store", "data", allow_duplicate=True),
        Input("account-switch-confirm-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def confirm_account_switch(
        n_clicks: int | None,
    ) -> tuple[bool, list[Any], str, dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], dict[str, str]]:
        res = handle_account_switch_confirm_logic(n_clicks=n_clicks)
        # Update client reference on app
        app.client = account_manager.get_client()
        return res
