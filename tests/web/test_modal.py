"""Tests for Stash Edit & Usage Modal, proportional math, and ledger rollback."""

from typing import Any
from unittest.mock import MagicMock, patch

import dash
import dash_bootstrap_components as dbc
import pytest
from dash import html
from dash.development.base_component import Component

from stashstats.web.app import create_app
from stashstats.web.callbacks.modal import (
    handle_history_rollback,
    handle_save_modal,
    handle_usage_preview_update,
    register_modal_callbacks,
)
from stashstats.web.components.modal import (
    apply_usage_to_stash,
    calculate_proportional_deduction,
    create_stash_modal,
    create_usage_history_table,
    create_usage_preview,
    rollback_usage_from_stash,
)


def find_component_by_id(tree: Any, component_id: Any) -> Component | None:
    """Recursively find a Dash component by its id (supports string or dict ids)."""
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


def find_all_components(tree: Any, predicate: Any) -> list[Component]:
    """Recursively find all components matching a predicate."""
    results: list[Component] = []
    if not isinstance(tree, Component) and not hasattr(tree, "to_plotly_json"):
        if isinstance(tree, list):
            for child in tree:
                results.extend(find_all_components(child, predicate))
        return results

    if predicate(tree):
        results.append(tree)

    children = getattr(tree, "children", None)
    if children is not None:
        if isinstance(children, list):
            for child in children:
                results.extend(find_all_components(child, predicate))
        else:
            results.extend(find_all_components(children, predicate))

    return results


# ---------------------------------------------------------------------------
# 1. Proportional Math & Inventory Logic Tests
# ---------------------------------------------------------------------------


def test_proportional_deduction_standard() -> None:
    """Verify proportional deduction calculations for standard usage."""
    calc = calculate_proportional_deduction(
        current_skeins=4.0,
        used_skeins=1.5,
        total_yards=840.0,
        total_grams=400.0,
        baseline_skeins=4.0,
    )
    assert calc["remaining_skeins"] == 2.5
    assert calc["deducted_yards"] == 315.0
    assert calc["remaining_yards"] == 525.0
    assert calc["deducted_grams"] == 150.0
    assert calc["remaining_grams"] == 250.0
    assert calc["is_valid"] is True
    assert calc["is_overdrawn"] is False
    assert calc["status_color"] == "success"


def test_proportional_deduction_with_per_skein_rates() -> None:
    """Verify proportional deduction using yards_per_skein and grams_per_skein."""
    calc = calculate_proportional_deduction(
        current_skeins=3.0,
        used_skeins=1.0,
        yards_per_skein=210.0,
        grams_per_skein=100.0,
    )
    assert calc["remaining_skeins"] == 2.0
    assert calc["deducted_yards"] == 210.0
    assert calc["remaining_yards"] == 420.0
    assert calc["deducted_grams"] == 100.0
    assert calc["remaining_grams"] == 200.0
    assert calc["is_valid"] is True


def test_proportional_deduction_exact_exhaustion() -> None:
    """Verify deduction when using exactly all remaining skeins."""
    calc = calculate_proportional_deduction(
        current_skeins=2.5,
        used_skeins=2.5,
        total_yards=500.0,
        total_grams=250.0,
        baseline_skeins=2.5,
    )
    assert calc["remaining_skeins"] == 0.0
    assert calc["remaining_yards"] == 0.0
    assert calc["remaining_grams"] == 0.0
    assert calc["is_valid"] is True
    assert calc["is_overdrawn"] is False


def test_proportional_deduction_overdrawn() -> None:
    """Verify warning state when used skeins exceeds current inventory."""
    calc = calculate_proportional_deduction(
        current_skeins=1.0,
        used_skeins=2.5,
        yards_per_skein=200.0,
    )
    assert calc["remaining_skeins"] == -1.5
    assert calc["is_valid"] is False
    assert calc["is_overdrawn"] is True
    assert calc["status_color"] in ("warning", "danger")


def test_proportional_deduction_zero_or_negative() -> None:
    """Verify handling when used skeins is zero or negative."""
    calc_zero = calculate_proportional_deduction(
        current_skeins=3.0,
        used_skeins=0.0,
        total_yards=600.0,
    )
    assert calc_zero["remaining_skeins"] == 3.0
    assert calc_zero["deducted_yards"] == 0.0
    assert calc_zero["is_valid"] is True

    calc_neg = calculate_proportional_deduction(
        current_skeins=3.0,
        used_skeins=-1.0,
    )
    assert calc_neg["is_valid"] is False


def test_apply_usage_to_stash() -> None:
    """Verify applying usage updates stash item fields and creates ledger record."""
    stash = {
        "id": 123,
        "name": "Rios",
        "skeins": 4.0,
        "total_yards": 840.0,
        "total_grams": 400.0,
        "yards_per_skein": 210.0,
        "grams_per_skein": 100.0,
        "stash_status": {"id": 1, "name": "In stash"},
    }

    updated_stash, ledger_entry = apply_usage_to_stash(
        stash_item=stash,
        used_skeins=1.5,
        date_used="2026-08-16",
        notes="Beanie project",
    )

    assert updated_stash["skeins"] == 2.5
    assert updated_stash["total_yards"] == 525.0
    assert updated_stash["total_grams"] == 250.0
    assert updated_stash["stash_status"]["name"] == "In stash"

    assert ledger_entry["skeins"] == -1.5
    assert ledger_entry["yards"] == -315.0
    assert ledger_entry["grams"] == -150.0
    assert ledger_entry["date"] == "2026-08-16"
    assert ledger_entry["notes"] == "Beanie project"


def test_apply_usage_to_stash_with_project_details() -> None:
    """Verify apply_usage_to_stash records project_name, project_id, and pattern_name in ledger."""
    stash = {
        "id": 123,
        "name": "Rios",
        "skeins": 4.0,
        "total_yards": 840.0,
        "total_grams": 400.0,
        "yards_per_skein": 210.0,
        "grams_per_skein": 100.0,
        "stash_status": {"id": 1, "name": "In stash"},
    }

    updated_stash, ledger_entry = apply_usage_to_stash(
        stash_item=stash,
        used_skeins=1.5,
        date_used="2026-08-16",
        notes="Knitted with stash yarn",
        project_name="Winter Beanie",
        project_id=501,
        pattern_name="Classic Ribbed Hat",
    )

    assert ledger_entry["project_name"] == "Winter Beanie"
    assert ledger_entry["project_id"] == 501
    assert ledger_entry["pattern_name"] == "Classic Ribbed Hat"


def test_apply_usage_to_stash_exhaustion_updates_status() -> None:
    """Verify applying usage that reduces inventory to 0 changes status to 'Used up'."""
    stash = {
        "id": 123,
        "skeins": 1.0,
        "total_yards": 200.0,
        "stash_status": {"id": 1, "name": "In stash"},
    }
    updated_stash, _ = apply_usage_to_stash(stash, used_skeins=1.0)
    assert updated_stash["skeins"] == 0.0
    assert updated_stash["stash_status"]["name"] == "Used up"


def test_apply_usage_to_stash_with_packs() -> None:
    """Verify apply_usage_to_stash correctly pulls quantity from primary_pack when skeins is None."""
    stash = {
        "id": 456,
        "name": "Bernat Satin Solids - Aqua",
        "skeins": None,
        "total_yards": None,
        "total_grams": None,
        "primary_pack": {
            "id": 999,
            "skeins": 6.0,
            "total_yards": 1200.0,
            "total_grams": 600.0,
        },
        "stash_status": {"id": 1, "name": "In stash"},
    }

    updated_stash, entry = apply_usage_to_stash(
        stash_item=stash,
        used_skeins=1.0,
        date_used="2026-08-17",
        notes="Crochet swatch",
    )

    assert updated_stash["skeins"] == 5.0
    assert updated_stash["total_yards"] == 1000.0
    assert updated_stash["total_grams"] == 500.0
    assert entry["skeins"] == -1.0
    assert entry["yards"] == -200.0
    assert entry["grams"] == -100.0
    assert entry["notes"] == "Crochet swatch"


def test_rollback_usage_from_stash() -> None:
    """Verify rolling back a usage entry restores quantities and removes entry."""
    stash = {
        "id": 123,
        "skeins": 2.5,
        "total_yards": 525.0,
        "total_grams": 250.0,
        "stash_status": {"id": 1, "name": "In stash"},
    }
    history = [
        {"id": "entry-1", "date": "2026-05-12", "skeins": -1.5, "yards": -315.0, "grams": -150.0},
        {"id": "entry-2", "date": "2026-06-01", "skeins": -0.5, "yards": -105.0, "grams": -50.0},
    ]

    updated_stash, updated_history = rollback_usage_from_stash(
        stash_item=stash,
        usage_index=0,
        history=history,
    )

    assert updated_stash["skeins"] == 4.0
    assert updated_stash["total_yards"] == 840.0
    assert updated_stash["total_grams"] == 400.0
    assert len(updated_history) == 1
    assert updated_history[0]["id"] == "entry-2"


def test_rollback_usage_restores_in_stash_status() -> None:
    """Verify rolling back from a 'Used up' stash entry restores 'In stash' status."""
    stash = {
        "id": 123,
        "skeins": 0.0,
        "total_yards": 0.0,
        "stash_status": {"id": 2, "name": "Used up"},
    }
    history = [
        {"id": "entry-1", "date": "2026-08-01", "skeins": -2.0, "yards": -400.0, "grams": -200.0}
    ]

    updated_stash, updated_history = rollback_usage_from_stash(stash, 0, history)
    assert updated_stash["skeins"] == 2.0
    assert updated_stash["stash_status"]["name"] == "In stash"
    assert len(updated_history) == 0


# ---------------------------------------------------------------------------
# 2. UI Component Rendering Tests
# ---------------------------------------------------------------------------


def test_create_stash_modal_structure() -> None:
    """Verify stash modal has header, tabs, inputs, and action buttons."""
    modal = create_stash_modal()
    assert isinstance(modal, dbc.Modal)
    assert getattr(modal, "id", None) == "stash-modal"

    # Header and title
    header = find_component_by_id(modal, "modal-header")
    assert header is not None
    title = find_component_by_id(modal, "modal-title")
    assert title is not None

    # Tabs
    tabs = find_component_by_id(modal, "modal-tabs")
    assert tabs is not None
    tab_ids = [getattr(tab, "tab_id", None) for tab in tabs.children if isinstance(tab, dbc.Tab)]
    assert "tab-edit-details" in tab_ids
    assert "tab-log-usage" in tab_ids

    # Tab 1 Edit fields
    assert find_component_by_id(modal, "modal-input-colorway") is not None
    assert find_component_by_id(modal, "modal-input-dye-lot") is not None
    assert find_component_by_id(modal, "modal-input-location") is not None
    assert find_component_by_id(modal, "modal-input-skeins") is not None
    assert find_component_by_id(modal, "modal-select-status") is not None
    assert find_component_by_id(modal, "modal-input-notes") is not None

    # Tab 2 Usage fields
    assert find_component_by_id(modal, "modal-usage-baseline") is not None
    assert find_component_by_id(modal, "modal-input-skeins-used") is not None
    assert find_component_by_id(modal, "modal-input-date-used") is not None
    assert find_component_by_id(modal, "modal-input-project-name") is not None
    assert find_component_by_id(modal, "modal-input-pattern-name") is not None
    assert find_component_by_id(modal, "modal-usage-preview") is not None
    assert find_component_by_id(modal, "modal-usage-history-table") is not None

    # Footer buttons
    assert find_component_by_id(modal, "modal-btn-delete") is not None
    assert find_component_by_id(modal, "modal-btn-cancel") is not None
    assert find_component_by_id(modal, "modal-btn-save") is not None

    # Stores
    assert find_component_by_id(modal, "modal-store-stash-item") is not None
    assert find_component_by_id(modal, "modal-store-history") is not None


def test_create_stash_modal_prepopulated() -> None:
    """Verify modal pre-populates fields when given a stash item."""
    sample_stash = {
        "id": 999,
        "yarn_name": "Rios",
        "brand_name": "Malabrigo",
        "colorway_name": "Diana",
        "dye_lot": "42",
        "location": "Box 3",
        "skeins": 3.0,
        "total_yards": 630.0,
        "total_grams": 300.0,
        "status": "In stash",
        "notes": "Purchased for sweater project",
        "created_at": "2026-02-10",
    }
    sample_history = [
        {"id": "entry-1", "date": "2026-05-12", "skeins": -1.0, "yards": -210.0, "grams": -100.0}
    ]

    modal = create_stash_modal(stash_item=sample_stash, history=sample_history, is_open=True)
    assert getattr(modal, "is_open", None) is True

    # Title check
    title = find_component_by_id(modal, "modal-title")
    assert title is not None
    title_str = str(title.to_plotly_json())
    assert "Malabrigo" in title_str or "Rios" in title_str or "Diana" in title_str

    # Values in inputs
    colorway_input = find_component_by_id(modal, "modal-input-colorway")
    assert colorway_input is not None
    assert getattr(colorway_input, "value", None) == "Diana"

    dye_lot_input = find_component_by_id(modal, "modal-input-dye-lot")
    assert dye_lot_input is not None
    assert getattr(dye_lot_input, "value", None) == "42"

    location_input = find_component_by_id(modal, "modal-input-location")
    assert location_input is not None
    assert getattr(location_input, "value", None) == "Box 3"

    skeins_input = find_component_by_id(modal, "modal-input-skeins")
    assert skeins_input is not None
    assert getattr(skeins_input, "value", None) == 3.0


def test_create_usage_history_table() -> None:
    """Verify history audit table renders rows and Delete buttons."""
    history = [
        {"id": "entry-1", "date": "2026-05-12", "skeins": -1.5, "yards": -315.0, "grams": -150.0},
        {"id": "entry-2", "date": "2026-06-01", "skeins": -0.5, "yards": -105.0, "grams": -50.0},
    ]
    table = create_usage_history_table(history)
    assert isinstance(table, dbc.Table)
    table_str = str(table.to_plotly_json())
    assert "2026-05-12" in table_str
    assert "-1.5" in table_str
    assert "-315" in table_str

    # Find delete buttons
    del_btns = find_all_components(
        table,
        lambda c: isinstance(getattr(c, "id", None), dict) and c.id.get("type") == "modal-btn-delete-usage"
    )
    assert len(del_btns) == 2


def test_create_usage_history_table_empty() -> None:
    """Verify empty history renders a friendly placeholder."""
    table = create_usage_history_table([])
    table_str = str(table.to_plotly_json())
    assert "No usage history" in table_str


def test_create_usage_preview_valid() -> None:
    """Verify preview card with valid remaining quantity."""
    preview = create_usage_preview(current_skeins=4.0, used_skeins=1.5, total_yards=840.0, total_grams=400.0)
    preview_str = str(preview.to_plotly_json())
    assert "Currently have: 4.0 skeins" in preview_str
    assert "Used: 1.5 skeins" in preview_str
    assert "Remaining: 2.5 skeins" in preview_str


def test_create_usage_preview_overdrawn() -> None:
    """Verify preview card shows warning/danger when overdrawn."""
    preview = create_usage_preview(current_skeins=1.0, used_skeins=2.5)
    preview_str = str(preview.to_plotly_json())
    assert "exceeds" in preview_str.lower() or "overdrawn" in preview_str.lower() or "remaining: -1.5" in preview_str.lower()


# ---------------------------------------------------------------------------
# 3. Callback Registration & Logic Tests
# ---------------------------------------------------------------------------


def test_modal_callbacks_registered() -> None:
    """Verify modal callbacks register cleanly on Dash app."""
    app = create_app()
    # Add modal to layout for callback binding
    app.layout.children.append(create_stash_modal())
    register_modal_callbacks(app)

    # Check callback map is populated
    assert len(app.callback_map) > 0
    registered_outputs = list(app.callback_map.keys())
    assert any("modal-usage-preview" in out for out in registered_outputs)
    assert any("modal-input-colorway" in out for out in registered_outputs)


def test_handle_usage_preview_update_with_packs() -> None:
    """Verify preview update pulls skeins from primary_pack when stash_item skeins is None."""
    stash_data = {
        "id": 456,
        "name": "Bernat Satin Solids - Aqua",
        "skeins": None,
        "primary_pack": {
            "skeins": 6.0,
            "total_yards": 1200.0,
            "total_grams": 600.0,
        },
    }

    preview = handle_usage_preview_update(used_skeins=1.0, stash_data=stash_data)
    preview_str = str(preview.to_plotly_json())
    assert "Currently have: 6.0 skeins" in preview_str
    assert "Used: 1.0 skeins" in preview_str
    assert "Remaining: 5.0 skeins" in preview_str
    assert "exceeds" not in preview_str.lower()


def test_handle_save_modal_calls_client_update_and_app_data() -> None:
    """Verify handle_save_modal invokes client.update_stash_item and client.set_app_data."""
    mock_client = MagicMock()
    mock_client.update_stash_item = MagicMock()
    mock_client.set_app_data = MagicMock()

    handle_save_modal(
        n_clicks=1,
        active_tab="tab-log-usage",
        colorway=None,
        dye_lot=None,
        location=None,
        skeins=None,
        status=None,
        notes="sample notes",
        used_skeins=1.0,
        date_used="2026-08-17",
        stash_data={"id": 123, "skeins": 6.0, "primary_pack": {"id": 999, "skeins": 6.0}},
        history_data=[],
        client=mock_client,
    )

    mock_client.update_stash_item.assert_called_once()
    _, kwargs = mock_client.update_stash_item.call_args
    assert kwargs.get("stash_id") == 123
    assert kwargs.get("skeins") == 5.0
    assert kwargs.get("pack_id") == 999
    mock_client.set_app_data.assert_called_once()


def test_handle_save_modal_with_project_metadata() -> None:
    """Verify handle_save_modal preserves project_name and pattern_name in new history entry."""
    is_open, updated_stash, updated_history = handle_save_modal(
        n_clicks=1,
        active_tab="tab-log-usage",
        colorway=None,
        dye_lot=None,
        location=None,
        skeins=None,
        status=None,
        notes="Hat project",
        used_skeins=1.5,
        date_used="2026-08-20",
        stash_data={"id": 123, "skeins": 4.0},
        history_data=[],
        project_name="Winter Beanie",
        pattern_name="Classic Ribbed Hat",
    )

    assert is_open is False
    assert len(updated_history) == 1
    assert updated_history[0]["project_name"] == "Winter Beanie"
    assert updated_history[0]["pattern_name"] == "Classic Ribbed Hat"
    assert updated_history[0]["skeins"] == -1.5


def test_handle_history_rollback_calls_client_update_and_app_data() -> None:
    """Verify handle_history_rollback invokes client.update_stash_item and client.set_app_data."""
    mock_client = MagicMock()
    mock_client.update_stash_item = MagicMock()
    mock_client.set_app_data = MagicMock()

    with patch.object(
        dash._callback_context.CallbackContext,
        "triggered_id",
        {"type": "modal-btn-delete-usage", "index": 0},
    ):
        handle_history_rollback(
            n_clicks_list=[1],
            stash_data={"id": 123, "skeins": 5.0, "primary_pack": {"id": 999, "skeins": 5.0}},
            history_data=[{"id": "entry-1", "skeins": -1.0}],
            used_skeins_val=0.0,
            client=mock_client,
        )

    mock_client.update_stash_item.assert_called_once()
    _, kwargs = mock_client.update_stash_item.call_args
    assert kwargs.get("stash_id") == 123
    assert kwargs.get("skeins") == 6.0
    assert kwargs.get("pack_id") == 999
    mock_client.set_app_data.assert_called_once()


def test_handle_save_modal_tab_log_usage_zero_skeins_prevents_update() -> None:
    """Verify handle_save_modal raises PreventUpdate if saving on log usage tab with 0 skeins."""
    with pytest.raises(dash.exceptions.PreventUpdate):
        handle_save_modal(
            n_clicks=1,
            active_tab="tab-log-usage",
            colorway=None,
            dye_lot=None,
            location=None,
            skeins=None,
            status=None,
            notes="",
            used_skeins=0.0,
            date_used="2026-08-18",
            stash_data={"id": 123, "skeins": 5.0},
            history_data=[],
        )


def test_create_linked_projects_table_empty():
    from stashstats.web.components.modal import create_linked_projects_table
    res = create_linked_projects_table([])
    assert isinstance(res, (html.Div, Component))


def test_create_linked_projects_table_with_records():
    from stashstats.models.analytics import ProjectUsageRecord
    from stashstats.web.components.modal import create_linked_projects_table

    records = [
        ProjectUsageRecord(
            project_id=101,
            project_name="Winter Hat",
            pattern_name="Classic Ribbed Hat",
            status_name="Finished",
            completed_date="2026-02-14",
            skeins_used=1.5,
            yards_used=315.0,
            grams_used=150.0,
        )
    ]
    table = create_linked_projects_table(records)
    assert isinstance(table, dbc.Table)


def test_create_stash_modal_with_linked_projects():
    from stashstats.models.analytics import ProjectUsageRecord
    records = [
        ProjectUsageRecord(
            project_id=101,
            project_name="Winter Hat",
            pattern_name="Classic Ribbed Hat",
            status_name="Finished",
            completed_date="2026-02-14",
            skeins_used=1.5,
            yards_used=315.0,
            grams_used=150.0,
        )
    ]
    modal = create_stash_modal(
        stash_item={"id": 123, "skeins": 5.0},
        linked_projects=records,
        is_open=True,
    )
    assert isinstance(modal, dbc.Modal)
    tbl = find_component_by_id(modal, "modal-linked-projects-table")
    assert tbl is not None


def test_create_usage_history_table_with_project():
    history = [
        {
            "id": "entry-1",
            "date": "2026-05-12",
            "skeins": -1.5,
            "yards": -315.0,
            "grams": -150.0,
            "project_name": "Winter Beanie",
            "pattern_name": "Classic Ribbed Hat",
        }
    ]
    table = create_usage_history_table(history)
    assert isinstance(table, dbc.Table)
    table_str = str(table.to_plotly_json())
    assert "Winter Beanie" in table_str





