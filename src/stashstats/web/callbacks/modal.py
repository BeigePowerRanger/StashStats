"""Reactive callbacks for Stash Edit & Usage Modal and ledger rollback."""

from typing import Any

import dash
from dash import Input, Output, State, ctx

from stashstats.web.components.modal import (
    apply_usage_to_stash,
    create_usage_history_table,
    create_usage_preview,
    rollback_usage_from_stash,
)


def handle_usage_preview_update(
    used_skeins: float | None,
    stash_data: dict[str, Any] | None,
) -> Any:
    """Compute and render live usage preview."""
    stash = stash_data or {}
    cur_skeins = stash.get("skeins")
    total_yards = stash.get("total_yards")
    total_grams = stash.get("total_grams")
    yards_per_skein = stash.get("yards_per_skein")
    grams_per_skein = stash.get("grams_per_skein")

    return create_usage_preview(
        current_skeins=cur_skeins,
        used_skeins=used_skeins or 0.0,
        total_yards=total_yards,
        total_grams=total_grams,
        yards_per_skein=yards_per_skein,
        grams_per_skein=grams_per_skein,
    )


def handle_history_rollback(
    n_clicks_list: list[int | None],
    stash_data: dict[str, Any] | None,
    history_data: list[dict[str, Any]] | None,
    used_skeins_val: float | None,
) -> tuple[dict[str, Any], list[dict[str, Any]], Any, float | None, Any]:
    """Execute rollback on clicked history index and return updated outputs."""
    stash = stash_data or {}
    history = history_data or []

    if not ctx.triggered_id or not isinstance(ctx.triggered_id, dict):
        raise dash.exceptions.PreventUpdate

    triggered_index = ctx.triggered_id.get("index")
    if triggered_index is None or not (0 <= triggered_index < len(history)):
        raise dash.exceptions.PreventUpdate

    updated_stash, updated_history = rollback_usage_from_stash(
        stash_item=stash,
        usage_index=triggered_index,
        history=history,
    )

    new_table = create_usage_history_table(updated_history)
    new_skeins = updated_stash.get("skeins")
    new_preview = create_usage_preview(
        current_skeins=new_skeins,
        used_skeins=used_skeins_val or 0.0,
        total_yards=updated_stash.get("total_yards"),
        total_grams=updated_stash.get("total_grams"),
    )

    return updated_stash, updated_history, new_table, new_skeins, new_preview


def handle_save_modal(
    n_clicks: int | None,
    active_tab: str | None,
    colorway: str | None,
    dye_lot: str | None,
    location: str | None,
    skeins: float | None,
    status: str | None,
    notes: str | None,
    used_skeins: float | None,
    date_used: str | None,
    stash_data: dict[str, Any] | None,
    history_data: list[dict[str, Any]] | None,
) -> tuple[bool, dict[str, Any], list[dict[str, Any]]]:
    """Process modal save action across Edit Details or Log Usage tabs."""
    if not n_clicks:
        raise dash.exceptions.PreventUpdate

    stash = dict(stash_data or {})
    history = list(history_data or [])

    if active_tab == "tab-log-usage" and used_skeins and float(used_skeins) > 0:
        stash, entry = apply_usage_to_stash(
            stash_item=stash,
            used_skeins=float(used_skeins),
            date_used=date_used,
            notes=notes,
        )
        history.insert(0, entry)
    else:
        # Update metadata fields from Tab 1
        if colorway is not None:
            stash["colorway_name"] = colorway
        if dye_lot is not None:
            stash["dye_lot"] = dye_lot
        if location is not None:
            stash["location"] = location
        if skeins is not None:
            stash["skeins"] = float(skeins)
        if status is not None:
            stash["stash_status"] = {"name": status}
        if notes is not None:
            stash["notes"] = notes

    # Close modal and commit state
    return False, stash, history


def register_modal_callbacks(app: dash.Dash) -> None:
    """Register reactive Dash callbacks for Stash Edit & Usage modal dialog.

    Args:
        app: dash.Dash application instance.
    """
    if getattr(app, "_modal_callbacks_registered", False):
        return
    app._modal_callbacks_registered = True  # type: ignore[attr-defined]

    @app.callback(
        Output("modal-usage-preview", "children"),
        Input("modal-input-skeins-used", "value"),
        State("modal-store-stash-item", "data"),
        prevent_initial_call=True,
    )
    def update_usage_preview(used_skeins: float | None, stash_data: dict[str, Any] | None) -> Any:
        return handle_usage_preview_update(used_skeins, stash_data)

    @app.callback(
        Output("modal-store-stash-item", "data", allow_duplicate=True),
        Output("modal-store-history", "data", allow_duplicate=True),
        Output("modal-usage-history-table", "children"),
        Output("modal-input-skeins", "value", allow_duplicate=True),
        Output("modal-usage-preview", "children", allow_duplicate=True),
        Input({"type": "modal-btn-delete-usage", "index": dash.ALL}, "n_clicks"),
        State("modal-store-stash-item", "data"),
        State("modal-store-history", "data"),
        State("modal-input-skeins-used", "value"),
        prevent_initial_call=True,
    )
    def rollback_history(
        n_clicks_list: list[int | None],
        stash_data: dict[str, Any] | None,
        history_data: list[dict[str, Any]] | None,
        used_skeins_val: float | None,
    ) -> Any:
        # Avoid firing on component mount if no click occurred
        if not any(n_clicks_list):
            raise dash.exceptions.PreventUpdate
        return handle_history_rollback(n_clicks_list, stash_data, history_data, used_skeins_val)

    @app.callback(
        Output("stash-modal", "is_open", allow_duplicate=True),
        Output("modal-store-stash-item", "data", allow_duplicate=True),
        Output("modal-store-history", "data", allow_duplicate=True),
        Input("modal-btn-save", "n_clicks"),
        State("modal-tabs", "active_tab"),
        State("modal-input-colorway", "value"),
        State("modal-input-dye-lot", "value"),
        State("modal-input-location", "value"),
        State("modal-input-skeins", "value"),
        State("modal-select-status", "value"),
        State("modal-input-notes", "value"),
        State("modal-input-skeins-used", "value"),
        State("modal-input-date-used", "value"),
        State("modal-store-stash-item", "data"),
        State("modal-store-history", "data"),
        prevent_initial_call=True,
    )
    def save_modal_changes(
        n_clicks: int | None,
        active_tab: str | None,
        colorway: str | None,
        dye_lot: str | None,
        location: str | None,
        skeins: float | None,
        status: str | None,
        notes: str | None,
        used_skeins: float | None,
        date_used: str | None,
        stash_data: dict[str, Any] | None,
        history_data: list[dict[str, Any]] | None,
    ) -> Any:
        return handle_save_modal(
            n_clicks,
            active_tab,
            colorway,
            dye_lot,
            location,
            skeins,
            status,
            notes,
            used_skeins,
            date_used,
            stash_data,
            history_data,
        )

    @app.callback(
        Output("stash-modal", "is_open", allow_duplicate=True),
        Input("modal-btn-cancel", "n_clicks"),
        prevent_initial_call=True,
    )
    def close_modal_cancel(n_clicks: int | None) -> bool:
        if not n_clicks:
            raise dash.exceptions.PreventUpdate
        return False
