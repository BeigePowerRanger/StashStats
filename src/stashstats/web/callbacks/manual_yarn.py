"""Reactive Dash callbacks for Manual Custom Yarn addition to stash."""

import logging
from datetime import UTC, datetime
from typing import Any

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, ctx, html

from stashstats.client import RavelryClient
from stashstats.models.stash import StashItem

logger = logging.getLogger("stashstats.web.manual_yarn")


def handle_manual_add_to_stash_logic(
    name: str | None,
    skeins: float | None,
    brand: str | None = None,
    weight: str | None = None,
    colorway: str | None = None,
    dyelot: str | None = None,
    yards: float | None = None,
    grams: float | None = None,
    location: str | None = None,
    date_added: str | None = None,
    status: str | None = "In stash",
    notes: str | None = None,
    client: RavelryClient | None = None,
    raw_stash_items: list[dict[str, Any]] | None = None,
) -> tuple[bool, Any, list[dict[str, Any]]]:
    """Execute manual yarn creation logic with API sync and local store fallback.

    Args:
        name: Custom yarn line name (required).
        skeins: Skein count (required > 0).
        brand: Optional manufacturer/dyer name.
        weight: Optional yarn weight category string.
        colorway: Optional colorway name.
        dyelot: Optional dye lot string.
        yards: Optional total yards.
        grams: Optional total grams.
        location: Optional storage location.
        date_added: Purchase or addition date.
        status: Status string (default 'In stash').
        notes: Optional personal notes.
        client: Optional authenticated RavelryClient.
        raw_stash_items: Current stash item dictionaries in browser store.

    Returns:
        Tuple of (is_success, status_component_or_message, updated_stash_items).
    """
    raw_stash = list(raw_stash_items) if raw_stash_items else []

    clean_name = (name or "").strip()
    if not clean_name:
        return (
            False,
            dbc.Alert(
                [html.I(className="bi bi-exclamation-triangle-fill me-2"), "Yarn Name is required."],
                color="danger",
                className="py-2 mb-0",
            ),
            raw_stash,
        )

    try:
        sk = float(skeins if skeins is not None else 1.0)
        if sk <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return (
            False,
            dbc.Alert(
                [html.I(className="bi bi-exclamation-triangle-fill me-2"), "Skeins must be a positive number."],
                color="danger",
                className="py-2 mb-0",
            ),
            raw_stash,
        )

    clean_brand = (brand or "").strip() or None
    clean_colorway = (colorway or "").strip() or None
    clean_dyelot = (dyelot or "").strip() or None
    clean_location = (location or "").strip() or None
    clean_notes = (notes or "").strip() or None
    clean_date = date_added or datetime.now(tz=UTC).date().isoformat()

    tot_yards = float(yards) if yards is not None and float(yards) > 0 else None
    tot_grams = float(grams) if grams is not None and float(grams) > 0 else None
    tot_meters = round(tot_yards * 0.9144, 2) if tot_yards else None

    status_map = {"In stash": 1, "Used up": 2, "Will trade/sell": 3, "Gone / Sold": 4}
    status_id = status_map.get(status or "In stash", 1)

    display_title = f"{clean_brand} {clean_name}".strip() if clean_brand else clean_name

    # 1. API Call if client is available
    if client is not None:
        try:
            created_item = client.create_stash_item(
                yarn_id=None,
                yarn_name=clean_name,
                yarn_company_name=clean_brand,
                colorway_name=clean_colorway,
                dye_lot=clean_dyelot,
                skeins=sk,
                total_grams=tot_grams,
                total_yards=tot_yards,
                location=clean_location,
                notes=clean_notes,
                purchased_date=clean_date,
                stash_status_id=status_id,
            )
            serialized = (
                created_item.model_dump()
                if hasattr(created_item, "model_dump")
                else created_item
            )
            # Ensure name and brand are retained
            if serialized.get("name") in ("untitled", "", None):
                serialized["name"] = display_title
            if not serialized.get("colorway_name"):
                serialized["colorway_name"] = clean_colorway

            updated_stash = [serialized] + raw_stash
            return (
                True,
                dbc.Alert(
                    [
                        html.I(className="bi bi-check-circle-fill me-2"),
                        f"Successfully added '{display_title}' to your Ravelry stash!",
                    ],
                    color="success",
                    className="py-2 mb-0",
                ),
                updated_stash,
            )
        except Exception as exc:
            logger.warning("Failed to create manual stash item via API, using local store: %s", exc)

    # 2. Local synthetic fallback
    synthetic_id = (
        max([it.get("id", 0) for it in raw_stash if isinstance(it, dict)] or [0])
        + 1001
    )

    new_stash_item: dict[str, Any] = {
        "id": synthetic_id,
        "name": display_title,
        "permalink": f"stash-{synthetic_id}",
        "colorway_name": clean_colorway,
        "dye_lot": clean_dyelot,
        "location": clean_location,
        "notes": clean_notes,
        "created_at": clean_date,
        "purchased": clean_date,
        "skeins": sk,
        "total_yards": tot_yards,
        "total_grams": tot_grams,
        "total_meters": tot_meters,
        "stash_status": {"id": status_id, "name": status or "In stash"},
        "yarn": {
            "id": 0,
            "name": clean_name,
            "yarn_company_name": clean_brand,
            "yarn_weight": {"id": 0, "name": weight or "Worsted"} if weight else None,
            "photos": [],
        },
        "packs": [
            {
                "id": synthetic_id + 5000,
                "stash_id": synthetic_id,
                "yarn_id": None,
                "colorway": clean_colorway,
                "dye_lot": clean_dyelot,
                "skeins": sk,
                "total_yards": tot_yards,
                "total_grams": tot_grams,
                "total_meters": tot_meters,
                "purchased_date": clean_date,
            }
        ],
    }

    validated_stash_item = StashItem.model_validate(new_stash_item).model_dump(mode="json")
    updated_stash = [validated_stash_item] + raw_stash
    return (
        True,
        dbc.Alert(
            [
                html.I(className="bi bi-check-circle-fill me-2"),
                f"Successfully added '{display_title}' to your local stash!",
            ],
            color="success",
            className="py-2 mb-0",
        ),
        updated_stash,
    )


def register_manual_yarn_callbacks(app: dash.Dash) -> None:
    """Register reactive Dash callbacks for Manual Custom Yarn addition modal.

    Args:
        app: dash.Dash application instance.
    """
    if getattr(app, "_manual_yarn_callbacks_registered", False):
        return
    app._manual_yarn_callbacks_registered = True  # type: ignore[attr-defined]

    @app.callback(
        Output("manual-yarn-modal", "is_open"),
        Output("manual-yarn-status-msg", "children"),
        Input("btn-open-manual-yarn-search", "n_clicks"),
        Input("btn-open-manual-yarn-stash", "n_clicks"),
        prevent_initial_call=True,
    )
    def open_manual_yarn_modal(n1: int | None, n2: int | None) -> tuple[bool, Any]:
        if not n1 and not n2:
            raise dash.exceptions.PreventUpdate
        return True, None

    @app.callback(
        Output("manual-yarn-modal", "is_open", allow_duplicate=True),
        Input("manual-yarn-btn-cancel", "n_clicks"),
        prevent_initial_call=True,
    )
    def close_manual_yarn_modal(n_clicks: int | None) -> bool:
        if not n_clicks:
            raise dash.exceptions.PreventUpdate
        return False

    @app.callback(
        Output("manual-yarn-modal", "is_open", allow_duplicate=True),
        Output("manual-yarn-status-msg", "children", allow_duplicate=True),
        Output("stash-raw-store", "data", allow_duplicate=True),
        Input("manual-yarn-btn-submit", "n_clicks"),
        State("manual-yarn-name", "value"),
        State("manual-yarn-brand", "value"),
        State("manual-yarn-weight", "value"),
        State("manual-yarn-colorway", "value"),
        State("manual-yarn-dyelot", "value"),
        State("manual-yarn-skeins", "value"),
        State("manual-yarn-yards", "value"),
        State("manual-yarn-grams", "value"),
        State("manual-yarn-location", "value"),
        State("manual-yarn-date", "value"),
        State("manual-yarn-status", "value"),
        State("manual-yarn-notes", "value"),
        State("stash-raw-store", "data"),
        prevent_initial_call=True,
    )
    def submit_manual_yarn(
        n_clicks: int | None,
        name: str | None,
        brand: str | None,
        weight: str | None,
        colorway: str | None,
        dyelot: str | None,
        skeins: float | None,
        yards: float | None,
        grams: float | None,
        location: str | None,
        date_added: str | None,
        status: str | None,
        notes: str | None,
        raw_stash_items: list[dict[str, Any]] | None,
    ) -> tuple[bool, Any, Any]:
        if not n_clicks:
            raise dash.exceptions.PreventUpdate

        client = getattr(app, "client", None)
        success, status_msg, updated_stash = handle_manual_add_to_stash_logic(
            name=name,
            skeins=skeins,
            brand=brand,
            weight=weight,
            colorway=colorway,
            dyelot=dyelot,
            yards=yards,
            grams=grams,
            location=location,
            date_added=date_added,
            status=status,
            notes=notes,
            client=client,
            raw_stash_items=raw_stash_items,
        )

        if not success:
            # Keep modal open so user can fix error
            return True, status_msg, dash.no_update

        # Close modal and commit new stash state
        return False, status_msg, updated_stash
