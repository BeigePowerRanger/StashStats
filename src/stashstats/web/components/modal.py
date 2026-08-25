import uuid
from datetime import UTC, datetime
from typing import Any

import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.development.base_component import Component

from stashstats.models.stash import StashItem

# ---------------------------------------------------------------------------
# 1. Proportional Math & Inventory Helper Functions
# ---------------------------------------------------------------------------


def calculate_proportional_deduction(
    current_skeins: float | None = 0.0,
    used_skeins: float | None = 0.0,
    yards_per_skein: float | None = None,
    grams_per_skein: float | None = None,
    total_yards: float | None = None,
    total_grams: float | None = None,
    baseline_skeins: float | None = None,
) -> dict[str, Any]:
    """Calculate proportional yardage, weight, and remaining quantities for stash usage.

    Args:
        current_skeins: Currently available skeins in stash.
        used_skeins: Amount of skeins consumed / deducted.
        yards_per_skein: Known length per skein in yards.
        grams_per_skein: Known weight per skein in grams.
        total_yards: Current or baseline total yards.
        total_grams: Current or baseline total grams.
        baseline_skeins: Original baseline skeins count for ratio calculation.

    Returns:
        Dict containing remaining quantities, deducted amounts, validation, and status flags.
    """
    cur_sk = float(current_skeins if current_skeins is not None else 0.0)
    usd_sk = float(used_skeins if used_skeins is not None else 0.0)

    if usd_sk < 0:
        return {
            "remaining_skeins": cur_sk,
            "deducted_yards": 0.0,
            "remaining_yards": total_yards,
            "deducted_grams": 0.0,
            "remaining_grams": total_grams,
            "is_valid": False,
            "is_overdrawn": False,
            "status_color": "danger",
            "message": "Used skeins cannot be negative.",
        }

    rem_sk = round(cur_sk - usd_sk, 4)
    is_overdrawn = rem_sk < 0
    is_valid = not is_overdrawn

    # Resolve yards per skein rate
    rate_yds: float | None = None
    if yards_per_skein is not None and yards_per_skein > 0:
        rate_yds = float(yards_per_skein)
    elif total_yards is not None and baseline_skeins is not None and float(baseline_skeins) > 0:
        rate_yds = float(total_yards) / float(baseline_skeins)
    elif total_yards is not None and cur_sk > 0:
        rate_yds = float(total_yards) / cur_sk

    # Resolve grams per skein rate
    rate_g: float | None = None
    if grams_per_skein is not None and grams_per_skein > 0:
        rate_g = float(grams_per_skein)
    elif total_grams is not None and baseline_skeins is not None and float(baseline_skeins) > 0:
        rate_g = float(total_grams) / float(baseline_skeins)
    elif total_grams is not None and cur_sk > 0:
        rate_g = float(total_grams) / cur_sk

    deducted_yards = round(usd_sk * rate_yds, 2) if rate_yds is not None else None
    if total_yards is not None:
        remaining_yards = round(float(total_yards) - (deducted_yards or 0.0), 2)
    elif rate_yds is not None:
        remaining_yards = round(rem_sk * rate_yds, 2)
    else:
        remaining_yards = None

    deducted_grams = round(usd_sk * rate_g, 2) if rate_g is not None else None
    if total_grams is not None:
        remaining_grams = round(float(total_grams) - (deducted_grams or 0.0), 2)
    elif rate_g is not None:
        remaining_grams = round(rem_sk * rate_g, 2)
    else:
        remaining_grams = None

    return {
        "remaining_skeins": rem_sk,
        "deducted_yards": deducted_yards,
        "remaining_yards": remaining_yards,
        "deducted_grams": deducted_grams,
        "remaining_grams": remaining_grams,
        "is_valid": is_valid,
        "is_overdrawn": is_overdrawn,
        "status_color": "success" if not is_overdrawn else "danger",
        "message": "Valid deduction" if not is_overdrawn else "Skeins used exceeds available inventory.",
    }


def apply_usage_to_stash(
    stash_item: dict[str, Any] | StashItem,
    used_skeins: float,
    date_used: str | None = None,
    notes: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Deduct used quantities from a stash record and generate a new ledger record.

    Args:
        stash_item: StashItem model instance or dict.
        used_skeins: Decimal number of skeins consumed.
        date_used: YYYY-MM-DD usage timestamp.
        notes: User project/usage notes.

    Returns:
        Tuple of (updated_stash_item_dict, new_history_entry_dict).
    """
    stash = stash_item.model_dump() if isinstance(stash_item, StashItem) else dict(stash_item)

    cur_skeins = stash.get("skeins")
    if cur_skeins is None and "primary_pack" in stash and stash["primary_pack"]:
        cur_skeins = stash["primary_pack"].get("skeins", 0.0)
    elif cur_skeins is None and stash.get("packs"):
        cur_skeins = sum(p.get("skeins", 0.0) or 0.0 for p in stash["packs"])

    total_yards = stash.get("total_yards")
    if total_yards is None and "primary_pack" in stash and stash["primary_pack"]:
        total_yards = stash["primary_pack"].get("total_yards")
    elif total_yards is None and stash.get("packs"):
        total_yards = sum(p.get("total_yards", 0.0) or 0.0 for p in stash["packs"])

    total_grams = stash.get("total_grams")
    if total_grams is None and "primary_pack" in stash and stash["primary_pack"]:
        total_grams = stash["primary_pack"].get("total_grams")
    elif total_grams is None and stash.get("packs"):
        total_grams = sum(p.get("total_grams", 0.0) or 0.0 for p in stash["packs"])

    calc = calculate_proportional_deduction(
        current_skeins=cur_skeins or 0.0,
        used_skeins=used_skeins,
        yards_per_skein=stash.get("yards_per_skein"),
        grams_per_skein=stash.get("grams_per_skein"),
        total_yards=total_yards,
        total_grams=total_grams,
    )

    today_iso = datetime.now(tz=UTC).date().isoformat()
    now_ts = datetime.now(tz=UTC).strftime("%Y/%m/%d %H:%M:%S +0000")
    usage_entry = {
        "id": f"entry-{uuid.uuid4().hex[:8]}",
        "date": date_used or today_iso,
        "timestamp": now_ts,
        "skeins": -abs(float(used_skeins)),
        "delta_skeins": -abs(float(used_skeins)),
        "yards": -abs(calc["deducted_yards"]) if calc["deducted_yards"] is not None else None,
        "grams": -abs(calc["deducted_grams"]) if calc["deducted_grams"] is not None else None,
        "total_yards": calc["remaining_yards"],
        "total_grams": calc["remaining_grams"],
        "notes": notes or "",
    }

    stash["skeins"] = calc["remaining_skeins"]
    if calc["remaining_yards"] is not None:
        stash["total_yards"] = calc["remaining_yards"]
    if calc["remaining_grams"] is not None:
        stash["total_grams"] = calc["remaining_grams"]

    if "primary_pack" in stash and isinstance(stash["primary_pack"], dict):
        stash["primary_pack"]["skeins"] = calc["remaining_skeins"]
        if calc["remaining_yards"] is not None:
            stash["primary_pack"]["total_yards"] = calc["remaining_yards"]
        if calc["remaining_grams"] is not None:
            stash["primary_pack"]["total_grams"] = calc["remaining_grams"]

    if "packs" in stash and isinstance(stash["packs"], list) and len(stash["packs"]) > 0:
        if isinstance(stash["packs"][0], dict):
            stash["packs"][0]["skeins"] = calc["remaining_skeins"]
            if calc["remaining_yards"] is not None:
                stash["packs"][0]["total_yards"] = calc["remaining_yards"]
            if calc["remaining_grams"] is not None:
                stash["packs"][0]["total_grams"] = calc["remaining_grams"]

    if calc["remaining_skeins"] <= 0:
        stash["stash_status"] = {"id": 2, "name": "Used up"}

    return stash, usage_entry


def rollback_usage_from_stash(
    stash_item: dict[str, Any] | StashItem,
    usage_index: int,
    history: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Roll back a past usage deduction from the history ledger and restore inventory.

    Args:
        stash_item: StashItem model instance or dict.
        usage_index: Zero-indexed position of entry in history list.
        history: Current list of history ledger entries.

    Returns:
        Tuple of (updated_stash_item_dict, updated_history_list).
    """
    stash = stash_item.model_dump() if isinstance(stash_item, StashItem) else dict(stash_item)
    updated_history = [dict(h) for h in history]

    if not (0 <= usage_index < len(updated_history)):
        return stash, updated_history

    entry = updated_history.pop(usage_index)
    skeins_to_restore = abs(float(entry.get("skeins", 0.0) or entry.get("delta_skeins", 0.0) or 0.0))
    yards_to_restore = abs(float(entry.get("yards", 0.0))) if entry.get("yards") is not None else None
    grams_to_restore = abs(float(entry.get("grams", 0.0))) if entry.get("grams") is not None else None

    cur_skeins = float(stash.get("skeins", 0.0) or 0.0)
    stash["skeins"] = round(cur_skeins + skeins_to_restore, 4)

    if yards_to_restore is not None and stash.get("total_yards") is not None:
        stash["total_yards"] = round(float(stash["total_yards"]) + yards_to_restore, 2)

    if grams_to_restore is not None and stash.get("total_grams") is not None:
        stash["total_grams"] = round(float(stash["total_grams"]) + grams_to_restore, 2)

    if "primary_pack" in stash and isinstance(stash["primary_pack"], dict):
        stash["primary_pack"]["skeins"] = stash["skeins"]
        if stash.get("total_yards") is not None:
            stash["primary_pack"]["total_yards"] = stash["total_yards"]
        if stash.get("total_grams") is not None:
            stash["primary_pack"]["total_grams"] = stash["total_grams"]

    if "packs" in stash and isinstance(stash["packs"], list) and len(stash["packs"]) > 0:
        if isinstance(stash["packs"][0], dict):
            stash["packs"][0]["skeins"] = stash["skeins"]
            if stash.get("total_yards") is not None:
                stash["packs"][0]["total_yards"] = stash["total_yards"]
            if stash.get("total_grams") is not None:
                stash["packs"][0]["total_grams"] = stash["total_grams"]

    # Restore active status if previously marked Used up
    current_status = stash.get("stash_status")
    status_name = current_status.get("name") if isinstance(current_status, dict) else str(current_status or "")
    if stash["skeins"] > 0 and status_name == "Used up":
        stash["stash_status"] = {"id": 1, "name": "In stash"}

    return stash, updated_history


# ---------------------------------------------------------------------------
# 2. UI Sub-Components
# ---------------------------------------------------------------------------


def create_usage_preview(
    current_skeins: float | None = 0.0,
    used_skeins: float | None = 0.0,
    total_yards: float | None = None,
    total_grams: float | None = None,
    yards_per_skein: float | None = None,
    grams_per_skein: float | None = None,
) -> Component:
    """Create live real-time preview card displaying calculated remaining inventory.

    Args:
        current_skeins: Current inventory count.
        used_skeins: Input usage deduction count.
        total_yards: Available total yards.
        total_grams: Available total grams.
        yards_per_skein: Yardage rate per skein.
        grams_per_skein: Grams rate per skein.

    Returns:
        dbc.Card component with formatted calculation preview.
    """
    calc = calculate_proportional_deduction(
        current_skeins=current_skeins,
        used_skeins=used_skeins,
        yards_per_skein=yards_per_skein,
        grams_per_skein=grams_per_skein,
        total_yards=total_yards,
        total_grams=total_grams,
    )

    cur_sk_val = float(current_skeins or 0.0)
    used_sk_val = float(used_skeins or 0.0)

    if calc["is_overdrawn"]:
        return dbc.Alert(
            [
                html.I(className="bi bi-exclamation-triangle-fill me-2"),
                html.Span(
                    f"Warning: Skeins used ({used_sk_val}) exceeds available inventory ({cur_sk_val} sk)! "
                    f"Remaining: {calc['remaining_skeins']} skeins.",
                    className="fw-semibold",
                ),
            ],
            color="danger",
            className="p-3 my-2",
        )

    # Details string for yards / weight
    details: list[str] = []
    if calc["remaining_yards"] is not None:
        details.append(f"{calc['remaining_yards']:,.0f} yds")
    if calc["remaining_grams"] is not None:
        details.append(f"{calc['remaining_grams']:,.0f} g")
    detail_str = f" ({' / '.join(details)})" if details else ""

    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.Span(f"Currently have: {cur_sk_val:.1f} skeins", className="text-light fw-medium"),
                    ],
                    className="mb-1",
                ),
                html.Div(
                    [
                        html.Span(f"Used: {used_sk_val:.1f} skeins", className="text-info me-2"),
                        html.I(className="bi bi-arrow-right text-muted me-2"),
                        html.Span(
                            f"Remaining: {calc['remaining_skeins']:.1f} skeins{detail_str}",
                            className="text-success fw-bold",
                        ),
                    ],
                    className="d-flex align-items-center flex-wrap",
                ),
            ],
            className="p-3",
        ),
        className="border-secondary bg-dark my-2",
    )


def create_usage_history_table(history: list[dict[str, Any]] | None = None) -> Component:
    """Create table component showing past usage history and rollback actions.

    Args:
        history: List of history ledger entries.

    Returns:
        dbc.Table or placeholder Div.
    """
    if not history:
        return html.Div(
            "No usage history recorded for this stash item.",
            className="text-muted fst-italic py-2 text-center border border-secondary rounded",
        )

    rows: list[html.Tr] = []
    for idx, entry in enumerate(history):
        skeins = entry.get("skeins") if entry.get("skeins") is not None else entry.get("delta_skeins", 0.0)
        sk_str = f"{skeins:+.2f} sk" if isinstance(skeins, (int, float)) else str(skeins)
        yards = entry.get("yards")
        yd_str = f"{yards:+.0f} yds" if yards is not None else "—"
        grams = entry.get("grams")
        g_str = f"{grams:+.0f} g" if grams is not None else "—"
        raw_date = entry.get("date") or entry.get("timestamp") or "—"
        entry_date = raw_date.split(" ")[0].replace("/", "-") if raw_date != "—" else "—"

        del_btn = dbc.Button(
            [html.I(className="bi bi-trash me-1"), "Delete"],
            id={"type": "modal-btn-delete-usage", "index": idx},
            color="outline-danger",
            size="sm",
            className="py-0 px-2",
        )

        rows.append(
            html.Tr(
                [
                    html.Td(entry_date, className="align-middle text-light"),
                    html.Td(sk_str, className="align-middle text-warning fw-semibold"),
                    html.Td(yd_str, className="align-middle text-muted"),
                    html.Td(g_str, className="align-middle text-muted"),
                    html.Td(del_btn, className="align-middle text-end"),
                ]
            )
        )

    table_header = html.Thead(
        html.Tr(
            [
                html.Th("Date", className="text-light"),
                html.Th("Skeins", className="text-light"),
                html.Th("Yards", className="text-light"),
                html.Th("Weight", className="text-light"),
                html.Th("Action", className="text-light text-end"),
            ]
        )
    )

    return dbc.Table(
        [table_header, html.Tbody(rows)],
        bordered=False,
        hover=True,
        responsive=True,
        striped=True,
        className="table-dark small mb-0",
    )


def create_linked_projects_table(
    linked_projects: list[Any] | None = None,
) -> Component:
    """Create table component showing projects that consumed this stash yarn.

    Args:
        linked_projects: List of ProjectUsageRecord or dicts.

    Returns:
        dbc.Table or placeholder Div.
    """
    if not linked_projects:
        return html.Div(
            "No projects linked to this stash yarn.",
            id="modal-linked-projects-empty",
            className="text-muted fst-italic py-2 text-center border border-secondary rounded",
        )

    rows: list[html.Tr] = []
    for p in linked_projects:
        p_name = p.project_name if hasattr(p, "project_name") else p.get("project_name", "Untitled")
        pattern = p.pattern_name if hasattr(p, "pattern_name") else p.get("pattern_name", "")
        status = p.status_name if hasattr(p, "status_name") else p.get("status_name", "In progress")
        comp_date = p.completed_date if hasattr(p, "completed_date") else p.get("completed_date", "—")
        if not comp_date:
            comp_date = "—"

        skeins_used = p.skeins_used if hasattr(p, "skeins_used") else p.get("skeins_used", 0.0)
        yards_used = p.yards_used if hasattr(p, "yards_used") else p.get("yards_used", 0.0)

        badge_color = "success" if (status or "").lower() == "finished" else "info"
        pattern_node = html.Small(f" ({pattern})", className="text-muted") if pattern else None

        rows.append(
            html.Tr(
                [
                    html.Td(
                        [
                            html.Span(p_name, className="text-light fw-medium"),
                            pattern_node,
                        ],
                        className="align-middle",
                    ),
                    html.Td(
                        dbc.Badge(status or "In progress", color=badge_color, className="px-2 py-1"),
                        className="align-middle",
                    ),
                    html.Td(comp_date, className="align-middle text-muted"),
                    html.Td(
                        f"{skeins_used:.1f} sk ({yards_used:,.0f} yds)" if yards_used else f"{skeins_used:.1f} sk",
                        className="align-middle text-warning text-end fw-semibold",
                    ),
                ]
            )
        )

    table_header = html.Thead(
        html.Tr(
            [
                html.Th("Project / Pattern", className="text-light"),
                html.Th("Status", className="text-light"),
                html.Th("Completed", className="text-light"),
                html.Th("Used", className="text-light text-end"),
            ]
        )
    )

    return dbc.Table(
        [table_header, html.Tbody(rows)],
        id="modal-linked-projects-table",
        bordered=False,
        hover=True,
        responsive=True,
        striped=True,
        className="table-dark small mb-0",
    )


# ---------------------------------------------------------------------------
# 3. Main Modal Dialog Layout
# ---------------------------------------------------------------------------


def create_stash_modal(
    stash_item: dict[str, Any] | StashItem | None = None,
    history: list[dict[str, Any]] | None = None,
    linked_projects: list[Any] | None = None,
    is_open: bool = False,
    modal_id: str = "stash-modal",
) -> dbc.Modal:
    """Create two-tab interactive Stash Edit & Usage modal dialog.

    Args:
        stash_item: Optional StashItem or dict to pre-populate.
        history: Optional list of usage history events.
        linked_projects: Optional list of linked ProjectUsageRecord or dicts.
        is_open: Initial open state of the modal.
        modal_id: Component ID for the modal.

    Returns:
        Configured dbc.Modal component.
    """
    item_dict = stash_item.model_dump() if isinstance(stash_item, StashItem) else (stash_item or {})
    hist_list = history or []
    projects_list = linked_projects or []

    # Extract field values with sensible fallbacks
    brand_name = item_dict.get("brand_name") or item_dict.get("yarn_company_name") or ""
    yarn_name = item_dict.get("yarn_name") or item_dict.get("name") or ""
    colorway_name = item_dict.get("colorway_name") or ""
    dye_lot = item_dict.get("dye_lot") or ""
    location = item_dict.get("location") or ""
    skeins = item_dict.get("skeins")
    if skeins is None and "primary_pack" in item_dict and item_dict["primary_pack"]:
        skeins = item_dict["primary_pack"].get("skeins")
    elif skeins is None and item_dict.get("packs"):
        skeins = sum(p.get("skeins", 0.0) or 0.0 for p in item_dict["packs"])

    total_yards = item_dict.get("total_yards")
    if total_yards is None and "primary_pack" in item_dict and item_dict["primary_pack"]:
        total_yards = item_dict["primary_pack"].get("total_yards")
    elif total_yards is None and item_dict.get("packs"):
        total_yards = sum(p.get("total_yards", 0.0) or 0.0 for p in item_dict["packs"])

    total_grams = item_dict.get("total_grams")
    if total_grams is None and "primary_pack" in item_dict and item_dict["primary_pack"]:
        total_grams = item_dict["primary_pack"].get("total_grams")
    elif total_grams is None and item_dict.get("packs"):
        total_grams = sum(p.get("total_grams", 0.0) or 0.0 for p in item_dict["packs"])

    notes = item_dict.get("notes") or ""
    created_at = item_dict.get("created_at") or "Unknown"

    status_obj = item_dict.get("stash_status") or item_dict.get("status")
    if isinstance(status_obj, dict):
        status_val = status_obj.get("name", "In stash")
    elif status_obj:
        status_val = str(status_obj)
    else:
        status_val = "In stash"

    title_parts = [p for p in [brand_name, yarn_name] if p]
    header_title = f"Edit Stash Entry: {' — '.join(title_parts)}" if title_parts else "Edit Stash Entry"
    if not title_parts and colorway_name:
        header_title = f"Edit Stash Entry: {colorway_name}"

    # Status dropdown options
    status_options = [
        {"label": "In stash", "value": "In stash"},
        {"label": "Used up", "value": "Used up"},
        {"label": "Gifted", "value": "Gifted"},
        {"label": "Gone / Sold", "value": "Gone / Sold"},
    ]

    # Baseline text for Tab 2
    baseline_parts: list[str] = []
    if skeins is not None:
        baseline_parts.append(f"{skeins:.1f} sk")
    if total_yards is not None:
        baseline_parts.append(f"{total_yards:,.0f} yds")
    if total_grams is not None:
        baseline_parts.append(f"{total_grams:,.0f} g")
    baseline_str = f"Originally stashed: {created_at} ({' / '.join(baseline_parts)})" if baseline_parts else f"Originally stashed: {created_at}"

    # Colorway options
    colorway_options = [{"label": colorway_name, "value": colorway_name}] if colorway_name else []

    # Tab 1: Edit Details
    tab_edit_details = dbc.Tab(
        label="Edit Details",
        tab_id="tab-edit-details",
        children=[
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Colorway", className="small text-light fw-bold"),
                            dcc.Dropdown(
                                id="modal-input-colorway",
                                value=colorway_name,
                                options=colorway_options,
                                placeholder="Select or enter colorway...",
                                searchable=True,
                                clearable=True,
                                className="dash-bootstrap",
                            ),
                        ],
                        md=6,
                        className="mb-3",
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Dye Lot", className="small text-light fw-bold"),
                            dbc.Input(
                                id="modal-input-dye-lot",
                                type="text",
                                value=dye_lot,
                                placeholder="Dye lot number/code...",
                                className="bg-dark text-light border-secondary",
                            ),
                        ],
                        md=6,
                        className="mb-3",
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Location", className="small text-light fw-bold"),
                            dbc.Input(
                                id="modal-input-location",
                                type="text",
                                value=location,
                                placeholder="Storage bin / shelf...",
                                className="bg-dark text-light border-secondary",
                            ),
                        ],
                        md=6,
                        className="mb-3",
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Total Skeins", className="small text-light fw-bold"),
                            dbc.Input(
                                id="modal-input-skeins",
                                type="number",
                                value=skeins,
                                step=0.1,
                                min=0,
                                placeholder="0.0",
                                className="bg-dark text-light border-secondary",
                            ),
                        ],
                        md=3,
                        className="mb-3",
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Status", className="small text-light fw-bold"),
                            dbc.Select(
                                id="modal-select-status",
                                options=status_options,
                                value=status_val,
                                className="bg-dark text-light border-secondary",
                            ),
                        ],
                        md=3,
                        className="mb-3",
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Notes", className="small text-light fw-bold"),
                            dbc.Textarea(
                                id="modal-input-notes",
                                value=notes,
                                placeholder="Add notes about this stash entry...",
                                rows=3,
                                className="bg-dark text-light border-secondary",
                            ),
                        ],
                        width=12,
                        className="mb-2",
                    )
                ]
            ),
        ],
        className="p-3",
    )

    # Tab 2: Log Usage
    tab_log_usage = dbc.Tab(
        label="Log Usage",
        tab_id="tab-log-usage",
        children=[
            html.Div(baseline_str, id="modal-usage-baseline", className="text-muted small mb-3"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Skeins Used", className="small text-light fw-bold"),
                            dbc.Input(
                                id="modal-input-skeins-used",
                                type="number",
                                step=0.1,
                                min=0,
                                placeholder="e.g. 1.5",
                                className="bg-dark text-light border-secondary",
                            ),
                        ],
                        md=6,
                        className="mb-3",
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Date Used", className="small text-light fw-bold"),
                            dbc.Input(
                                id="modal-input-date-used",
                                type="date",
                                value=datetime.now(tz=UTC).date().isoformat(),
                                className="bg-dark text-light border-secondary",
                            ),
                        ],
                        md=6,
                        className="mb-3",
                    ),
                ]
            ),
            html.Div(
                id="modal-usage-preview",
                children=create_usage_preview(
                    current_skeins=skeins,
                    used_skeins=0.0,
                    total_yards=total_yards,
                    total_grams=total_grams,
                ),
            ),
            html.Div(
                id="modal-history-container",
                className="mt-4",
                children=[
                    html.H6("Usage History", className="text-light fw-bold mb-2"),
                    html.Div(
                        id="modal-usage-history-table",
                        children=create_usage_history_table(hist_list),
                    ),
                ],
            ),
            html.Div(
                id="modal-linked-projects-container",
                className="mt-4",
                children=[
                    html.H6("Projects Made with this Yarn", className="text-light fw-bold mb-2"),
                    html.Div(
                        id="modal-linked-projects-content",
                        children=create_linked_projects_table(projects_list),
                    ),
                ],
            ),
        ],
        className="p-3",
    )

    tabs = dbc.Tabs(
        id="modal-tabs",
        active_tab="tab-edit-details",
        children=[tab_edit_details, tab_log_usage],
        className="border-bottom border-secondary",
    )

    modal_header = dbc.ModalHeader(
        dbc.ModalTitle(header_title, id="modal-title", className="fw-bold text-light"),
        id="modal-header",
        close_button=True,
        className="border-secondary bg-dark",
    )

    modal_body = dbc.ModalBody(
        [
            tabs,
            dcc.Store(id="modal-store-stash-item", data=item_dict),
            dcc.Store(id="modal-store-history", data=hist_list),
            dcc.Store(
                id="modal-store-linked-projects",
                data=[p.model_dump() if hasattr(p, "model_dump") else p for p in projects_list],
            ),
            dcc.Store(id="modal-feedback-store", data=None),
        ],
        id="modal-body",
        className="bg-dark text-light p-0",
    )

    modal_footer = dbc.ModalFooter(
        [
            dbc.Button(
                [html.I(className="bi bi-trash me-1"), "Delete Entry"],
                id="modal-btn-delete",
                color="danger",
                className="me-auto",
            ),
            dbc.Button("Cancel", id="modal-btn-cancel", color="secondary", className="me-2"),
            dbc.Button(
                [html.I(className="bi bi-check2 me-1"), "Save Changes"],
                id="modal-btn-save",
                color="success",
            ),
        ],
        id="modal-footer",
        className="border-secondary bg-dark",
    )

    return dbc.Modal(
        [modal_header, modal_body, modal_footer],
        id=modal_id,
        is_open=is_open,
        size="lg",
        centered=True,
        className="stash-edit-modal",
    )
