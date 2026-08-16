"""Reactive callbacks for Personal Stash filtering, sorting, pagination, and sync."""

from datetime import UTC, datetime
from typing import Any

import dash
from dash import Input, Output, State

from stashstats.web.components.stash import (
    create_grouped_stash_accordion,
    filter_stash_groups,
    group_stash_items,
    paginate_stash_groups,
    sort_stash_groups,
)


def update_stash_view_logic(
    search_query: str | None,
    sort_by: str | None,
    active_page: int | None,
    raw_data: list[dict[str, Any]] | None,
) -> tuple[Any, int, int, str]:
    """Filter, sort, and paginate stash items based on UI controls."""
    items = raw_data or []
    groups = group_stash_items(items)
    filtered = filter_stash_groups(groups, search_query)
    sorted_groups = sort_stash_groups(filtered, sort_by or "brand_asc")

    page_num = active_page if active_page and active_page > 0 else 1
    paginated_groups, total_pages = paginate_stash_groups(
        sorted_groups, page=page_num, page_size=10
    )
    clamped_page = max(1, min(page_num, total_pages))

    accordion = create_grouped_stash_accordion(paginated_groups)
    info_text = f"Showing page {clamped_page} of {total_pages} ({len(filtered)} parent yarns)"

    return accordion, total_pages, clamped_page, info_text


def handle_stash_sync_logic(
    n_clicks: int | None,
    raw_data: list[dict[str, Any]] | None,
) -> tuple[str, str, str]:
    """Handle Sync Now button click to synchronize with Ravelry."""
    if not n_clicks:
        raise dash.exceptions.PreventUpdate

    now_str = datetime.now(UTC).strftime("Today %H:%M")
    return "Synced", "success", f"Last synced: {now_str}"


def register_stash_callbacks(app: dash.Dash) -> None:
    """Register all interactive callbacks for the Personal Stash view.

    Args:
        app: The Dash application instance.
    """
    if getattr(app, "_stash_callbacks_registered", False):
        return
    app._stash_callbacks_registered = True  # type: ignore[attr-defined]

    @app.callback(
        Output("stash-list-container", "children"),
        Output("stash-pagination", "max_value"),
        Output("stash-pagination", "active_page"),
        Output("stash-pagination-info", "children"),
        Input("stash-search-input", "value"),
        Input("stash-sort-dropdown", "value"),
        Input("stash-pagination", "active_page"),
        Input("stash-raw-store", "data"),
        prevent_initial_call=False,
    )
    def update_stash_view(
        search_query: str | None,
        sort_by: str | None,
        active_page: int | None,
        raw_data: list[dict[str, Any]] | None,
    ) -> tuple[Any, int, int, str]:
        return update_stash_view_logic(search_query, sort_by, active_page, raw_data)

    @app.callback(
        Output("stash-pending-badge", "children"),
        Output("stash-pending-badge", "color"),
        Output("stash-last-synced", "children"),
        Input("stash-sync-btn", "n_clicks"),
        State("stash-raw-store", "data"),
        prevent_initial_call=True,
    )
    def handle_stash_sync(
        n_clicks: int | None,
        raw_data: list[dict[str, Any]] | None,
    ) -> tuple[str, str, str]:
        return handle_stash_sync_logic(n_clicks, raw_data)
