import json
import logging
from datetime import UTC, datetime
from typing import Any

import dash
from dash import Input, Output, State, ctx

from stashstats.web.components.modal import (
    apply_usage_to_stash,
    create_usage_history_table,
    create_usage_preview,
    rollback_usage_from_stash,
)

logger = logging.getLogger("stashstats.web.modal")


def handle_usage_preview_update(
    used_skeins: float | None,
    stash_data: dict[str, Any] | None,
) -> Any:
    """Compute and render live usage preview."""
    stash = stash_data or {}
    cur_skeins = stash.get("skeins")
    if cur_skeins is None and "primary_pack" in stash and stash["primary_pack"]:
        cur_skeins = stash["primary_pack"].get("skeins")
    elif cur_skeins is None and stash.get("packs"):
        cur_skeins = sum(p.get("skeins", 0.0) or 0.0 for p in stash["packs"] if isinstance(p, dict))

    total_yards = stash.get("total_yards")
    if total_yards is None and "primary_pack" in stash and stash["primary_pack"]:
        total_yards = stash["primary_pack"].get("total_yards")
    elif total_yards is None and stash.get("packs"):
        total_yards = sum(p.get("total_yards", 0.0) or 0.0 for p in stash["packs"] if isinstance(p, dict))

    total_grams = stash.get("total_grams")
    if total_grams is None and "primary_pack" in stash and stash["primary_pack"]:
        total_grams = stash["primary_pack"].get("total_grams")
    elif total_grams is None and stash.get("packs"):
        total_grams = sum(p.get("total_grams", 0.0) or 0.0 for p in stash["packs"] if isinstance(p, dict))

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
    client: Any = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], Any, float | None, Any]:
    """Execute rollback on clicked history index and return updated outputs."""
    stash = stash_data or {}
    history = history_data or []

    if not ctx.triggered_id or not isinstance(ctx.triggered_id, dict):
        raise dash.exceptions.PreventUpdate

    triggered_index = ctx.triggered_id.get("index")
    if triggered_index is None or not (0 <= triggered_index < len(history)):
        raise dash.exceptions.PreventUpdate

    logger.info(f"Rolling back history index {triggered_index} for stash_id={stash.get('id')}")
    updated_stash, updated_history = rollback_usage_from_stash(
        stash_item=stash,
        usage_index=triggered_index,
        history=history,
    )
    updated_stash["history"] = updated_history
    updated_stash["usage_history"] = updated_history

    # Sync with Ravelry if client is present
    if client and updated_stash.get("id"):
        try:
            status_val = updated_stash.get("stash_status")
            status_id = status_val.get("id") if isinstance(status_val, dict) else (2 if float(updated_stash.get("skeins") or 0.0) <= 0 else 1)
            pack_id = updated_stash.get("primary_pack", {}).get("id") if isinstance(updated_stash.get("primary_pack"), dict) else None
            client.update_stash_item(
                stash_id=updated_stash["id"],
                skeins=updated_stash.get("skeins"),
                total_yards=updated_stash.get("total_yards"),
                total_grams=updated_stash.get("total_grams"),
                stash_status_id=status_id,
                pack_id=pack_id,
                notes=updated_stash.get("notes"),
            )
            logger.debug(f"Updated stash item {updated_stash['id']} in Ravelry API after rollback")
        except Exception as e:
            logger.warning(f"Failed to update stash item in Ravelry API after rollback: {e}")

        try:
            key = f"stash_history_{updated_stash['id']}"
            client.set_app_data(**{key: json.dumps(updated_history)})
            logger.debug(f"Updated Ravelry app_data {key} after rollback")
        except Exception as e:
            logger.warning(f"Failed to update Ravelry app_data after rollback: {e}")

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
    project_name: str | None = None,
    pattern_name: str | None = None,
    client: Any = None,
) -> tuple[bool, dict[str, Any], list[dict[str, Any]]]:
    """Process modal save action across Edit Details or Log Usage tabs."""
    if not n_clicks:
        raise dash.exceptions.PreventUpdate

    stash = dict(stash_data or {})
    history = list(history_data or [])

    if active_tab == "tab-log-usage":
        if not used_skeins or float(used_skeins) <= 0:
            raise dash.exceptions.PreventUpdate

        logger.info(f"Logging usage for stash_id={stash.get('id')}: {used_skeins} skeins on {date_used}")
        stash, entry = apply_usage_to_stash(
            stash_item=stash,
            used_skeins=float(used_skeins),
            date_used=date_used,
            notes=notes,
            project_name=project_name,
            pattern_name=pattern_name,
        )
        history.insert(0, entry)
        stash["history"] = history
        stash["usage_history"] = history

        if client and stash.get("id"):
            try:
                status_val = stash.get("stash_status")
                status_id = status_val.get("id") if isinstance(status_val, dict) else (2 if float(stash.get("skeins") or 0.0) <= 0 else 1)
                pack_id = stash.get("primary_pack", {}).get("id") if isinstance(stash.get("primary_pack"), dict) else None
                client.update_stash_item(
                    stash_id=stash["id"],
                    skeins=stash.get("skeins"),
                    total_yards=stash.get("total_yards"),
                    total_grams=stash.get("total_grams"),
                    stash_status_id=status_id,
                    pack_id=pack_id,
                    notes=stash.get("notes"),
                )
                logger.debug(f"Updated stash item {stash['id']} quantities in Ravelry API")
            except Exception as e:
                logger.warning(f"Failed to update stash item in Ravelry API: {e}")

            try:
                # Save snapshot to Ravelry app_data
                key = f"stash_history_{stash['id']}"
                client.set_app_data(**{key: json.dumps(history)})
                logger.debug(f"Saved usage history to Ravelry app_data {key}")
            except Exception as e:
                logger.warning(f"Failed to save history to Ravelry app_data: {e}")
    else:
        logger.info(f"Saving metadata details for stash_id={stash.get('id')}")
        # Update metadata fields from Tab 1
        if colorway is not None:
            stash["colorway_name"] = colorway
            if "primary_pack" in stash and isinstance(stash["primary_pack"], dict):
                stash["primary_pack"]["colorway"] = colorway
        if dye_lot is not None:
            stash["dye_lot"] = dye_lot
            if "primary_pack" in stash and isinstance(stash["primary_pack"], dict):
                stash["primary_pack"]["dye_lot"] = dye_lot
        if location is not None:
            stash["location"] = location
        if skeins is not None:
            stash["skeins"] = float(skeins)
            if "primary_pack" in stash and isinstance(stash["primary_pack"], dict):
                stash["primary_pack"]["skeins"] = float(skeins)
        if status is not None:
            status_map = {"In stash": 1, "Used up": 2, "Will trade/sell": 3, "Gone / Sold": 4}
            status_id = status_map.get(status, 1) if isinstance(status, str) else int(status)
            stash["stash_status"] = {"id": status_id, "name": status}
        else:
            status_id = None
        if notes is not None:
            stash["notes"] = notes

        if client and stash.get("id"):
            try:
                pack_id = stash.get("primary_pack", {}).get("id") if isinstance(stash.get("primary_pack"), dict) else None
                client.update_stash_item(
                    stash_id=stash["id"],
                    colorway_name=colorway,
                    dye_lot=dye_lot,
                    location=location,
                    skeins=float(skeins) if skeins is not None else None,
                    stash_status_id=status_id,
                    pack_id=pack_id,
                    notes=notes,
                )
                logger.debug(f"Updated stash item {stash['id']} in Ravelry API")
            except Exception as e:
                logger.warning(f"Failed to update stash item in Ravelry API: {e}")

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
        Output("stash-modal", "is_open"),
        Output("modal-title", "children"),
        Output("modal-store-stash-item", "data"),
        Output("modal-store-history", "data"),
        Output("modal-input-colorway", "value"),
        Output("modal-input-dye-lot", "value"),
        Output("modal-input-location", "value"),
        Output("modal-input-skeins", "value"),
        Output("modal-select-status", "value"),
        Output("modal-input-notes", "value"),
        Output("modal-usage-baseline", "children"),
        Output("modal-input-skeins-used", "value"),
        Output("modal-input-date-used", "value"),
        Output("modal-usage-preview", "children", allow_duplicate=True),
        Output("modal-usage-history-table", "children", allow_duplicate=True),
        Input({"type": "stash-edit-btn", "index": dash.ALL}, "n_clicks"),
        State("stash-raw-store", "data"),
        prevent_initial_call=True,
    )
    def open_stash_modal(
        n_clicks_list: list[int | None],
        raw_data: list[dict[str, Any]] | None,
    ) -> Any:
        if not any(n_clicks_list):
            raise dash.exceptions.PreventUpdate

        triggered_id = dash.ctx.triggered_id
        if not triggered_id or not isinstance(triggered_id, dict):
            raise dash.exceptions.PreventUpdate

        stash_id = triggered_id.get("index")
        if not stash_id:
            raise dash.exceptions.PreventUpdate

        raw_items = raw_data or []
        target_item = None
        for it in raw_items:
            if it.get("id") == stash_id or str(it.get("id")) == str(stash_id):
                target_item = it
                break

        if not target_item:
            raise dash.exceptions.PreventUpdate

        brand_name = (
            target_item.get("yarn", {}).get("yarn_company_name")
            if isinstance(target_item.get("yarn"), dict)
            else (target_item.get("yarn_company_name") or target_item.get("brand_name") or "")
        )
        yarn_name = (
            target_item.get("yarn", {}).get("name")
            if isinstance(target_item.get("yarn"), dict)
            else (target_item.get("yarn_name") or target_item.get("name") or "")
        )
        colorway_name = target_item.get("colorway_name") or (
            target_item.get("primary_pack", {}).get("colorway")
            if isinstance(target_item.get("primary_pack"), dict)
            else ""
        ) or ""

        title = f"Edit {brand_name} {yarn_name} — {colorway_name}".strip(" —")

        dye_lot = target_item.get("dye_lot") or (
            target_item.get("primary_pack", {}).get("dye_lot")
            if isinstance(target_item.get("primary_pack"), dict)
            else ""
        ) or ""
        location = target_item.get("location") or ""

        skeins = target_item.get("skeins")
        if skeins is None and isinstance(target_item.get("primary_pack"), dict):
            skeins = target_item["primary_pack"].get("skeins")
        elif skeins is None and target_item.get("packs"):
            skeins = sum(p.get("skeins", 0.0) or 0.0 for p in target_item["packs"] if isinstance(p, dict))
        skeins_val = float(skeins) if skeins is not None else 0.0

        total_yards = target_item.get("total_yards")
        if total_yards is None and isinstance(target_item.get("primary_pack"), dict):
            total_yards = target_item["primary_pack"].get("total_yards")
        elif total_yards is None and target_item.get("packs"):
            total_yards = sum(p.get("total_yards", 0.0) or 0.0 for p in target_item["packs"] if isinstance(p, dict))

        total_grams = target_item.get("total_grams")
        if total_grams is None and isinstance(target_item.get("primary_pack"), dict):
            total_grams = target_item["primary_pack"].get("total_grams")
        elif total_grams is None and target_item.get("packs"):
            total_grams = sum(p.get("total_grams", 0.0) or 0.0 for p in target_item["packs"] if isinstance(p, dict))

        status_name = (
            target_item.get("stash_status", {}).get("name")
            if isinstance(target_item.get("stash_status"), dict)
            else (target_item.get("status") or "In stash")
        )
        notes = target_item.get("notes") or ""

        baseline_text = f"Baseline inventory: {skeins_val:g} skeins"

        history: list[dict[str, Any]] = []
        client = getattr(app, "client", None)
        if client:
            try:
                hist_obj = client.get_stash_history(stash_id)
                history = [e.model_dump() for e in hist_obj.entries]
            except Exception:
                pass

        preview = create_usage_preview(
            current_skeins=skeins_val,
            used_skeins=0.0,
            total_yards=total_yards,
            total_grams=total_grams,
        )
        history_table = create_usage_history_table(history)
        today_iso = datetime.now(tz=UTC).date().isoformat()

        return (
            True,
            title,
            target_item,
            history,
            colorway_name,
            dye_lot,
            location,
            skeins_val,
            status_name,
            notes,
            baseline_text,
            0.0,
            today_iso,
            preview,
            history_table,
        )

    @app.callback(
        Output("modal-input-colorway", "options"),
        Input("modal-store-stash-item", "data"),
        prevent_initial_call=True,
    )
    def update_colorway_dropdown_options(stash_data: dict[str, Any] | None) -> list[dict[str, str]]:
        if not stash_data:
            return []

        existing_colorway = stash_data.get("colorway_name") or (
            stash_data.get("primary_pack", {}).get("colorway")
            if isinstance(stash_data.get("primary_pack"), dict)
            else ""
        ) or ""

        options: list[dict[str, str]] = []
        if existing_colorway:
            options.append({"label": existing_colorway, "value": existing_colorway})

        yarn_info = stash_data.get("yarn")
        yarn_id = None
        if isinstance(yarn_info, dict):
            yarn_id = yarn_info.get("id")
        elif stash_data.get("yarn_id"):
            yarn_id = stash_data.get("yarn_id")

        client = getattr(app, "client", None)
        if client and yarn_id:
            try:
                yarn_detail = client.get_yarn_details(yarn_id)
                seen_names = {opt["value"] for opt in options}
                for cw in yarn_detail.yarn.colorways:
                    if cw.name and cw.name not in seen_names:
                        options.append({"label": cw.name, "value": cw.name})
                        seen_names.add(cw.name)
            except Exception as e:
                logger.debug(f"Failed to fetch yarn colorways for dropdown: {e}")

        return options

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
        if not any(n_clicks_list):
            raise dash.exceptions.PreventUpdate
        client = getattr(app, "client", None)
        return handle_history_rollback(
            n_clicks_list, stash_data, history_data, used_skeins_val, client=client
        )

    @app.callback(
        Output("stash-modal", "is_open", allow_duplicate=True),
        Output("modal-store-stash-item", "data", allow_duplicate=True),
        Output("modal-store-history", "data", allow_duplicate=True),
        Output("stash-raw-store", "data", allow_duplicate=True),
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
        State("modal-input-project-name", "value"),
        State("modal-input-pattern-name", "value"),
        State("modal-store-stash-item", "data"),
        State("modal-store-history", "data"),
        State("stash-raw-store", "data"),
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
        project_name: str | None,
        pattern_name: str | None,
        stash_data: dict[str, Any] | None,
        history_data: list[dict[str, Any]] | None,
        raw_stash_items: list[dict[str, Any]] | None,
    ) -> Any:
        client = getattr(app, "client", None)
        is_open, updated_stash, updated_history = handle_save_modal(
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
            project_name=project_name,
            pattern_name=pattern_name,
            client=client,
        )

        items_list = [dict(it) for it in (raw_stash_items or [])]
        if updated_stash.get("id"):
            for i, it in enumerate(items_list):
                if str(it.get("id")) == str(updated_stash["id"]):
                    items_list[i] = updated_stash
                    break

        return is_open, updated_stash, updated_history, items_list

    @app.callback(
        Output("stash-modal", "is_open", allow_duplicate=True),
        Input("modal-btn-cancel", "n_clicks"),
        prevent_initial_call=True,
    )
    def close_modal_cancel(n_clicks: int | None) -> bool:
        if not n_clicks:
            raise dash.exceptions.PreventUpdate
        return False
