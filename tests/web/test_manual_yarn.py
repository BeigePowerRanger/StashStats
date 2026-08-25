"""Tests for Manual Custom Yarn addition modal, layout, validation, and callbacks."""

from unittest.mock import MagicMock

import dash
from dash import html
import dash_bootstrap_components as dbc

from stashstats.web.components.manual_yarn_modal import (
    create_manual_yarn_modal,
    DARK_INPUT_STYLE,
    STATUS_OPTIONS,
    YARN_WEIGHT_OPTIONS,
)
from stashstats.web.callbacks.manual_yarn import (
    handle_manual_add_to_stash_logic,
    register_manual_yarn_callbacks,
)
from stashstats.web.app import create_app


def test_create_manual_yarn_modal_structure() -> None:
    """Verify create_manual_yarn_modal renders structured form controls."""
    modal = create_manual_yarn_modal(is_open=True)
    assert isinstance(modal, dbc.Modal)
    assert modal.id == "manual-yarn-modal"
    assert modal.is_open is True

    json_repr = str(modal.to_plotly_json())
    assert "manual-yarn-name" in json_repr
    assert "manual-yarn-brand" in json_repr
    assert "manual-yarn-weight" in json_repr
    assert "manual-yarn-colorway" in json_repr
    assert "manual-yarn-dyelot" in json_repr
    assert "manual-yarn-skeins" in json_repr
    assert "manual-yarn-yards" in json_repr
    assert "manual-yarn-grams" in json_repr
    assert "manual-yarn-location" in json_repr
    assert "manual-yarn-date" in json_repr
    assert "manual-yarn-status" in json_repr
    assert "manual-yarn-notes" in json_repr
    assert "manual-yarn-btn-cancel" in json_repr
    assert "manual-yarn-btn-submit" in json_repr


def test_handle_manual_add_to_stash_logic_validation_name() -> None:
    """Verify validation error when yarn name is empty."""
    success, msg, raw_stash = handle_manual_add_to_stash_logic(
        name="",
        skeins=1.0,
        raw_stash_items=[],
    )
    assert success is False
    assert "Yarn Name is required" in str(msg)
    assert len(raw_stash) == 0


def test_handle_manual_add_to_stash_logic_validation_skeins() -> None:
    """Verify validation error when skein count is zero or negative."""
    success, msg, raw_stash = handle_manual_add_to_stash_logic(
        name="Handspun Merino",
        skeins=0.0,
        raw_stash_items=[],
    )
    assert success is False
    assert "Skeins must be a positive number" in str(msg)
    assert len(raw_stash) == 0


def test_handle_manual_add_to_stash_logic_offline_fallback() -> None:
    """Verify successful local synthesized stash creation when offline/client is None."""
    existing_items = [{"id": 5, "name": "Cascade 220", "skeins": 2.0}]

    success, msg, updated_stash = handle_manual_add_to_stash_logic(
        name="Artisan Singles",
        brand="Indie Dyer",
        weight="Fingering",
        colorway="Sunset Glow",
        dyelot="Lot A",
        skeins=3.0,
        yards=1200.0,
        grams=300.0,
        location="Top Shelf",
        status="In stash",
        notes="Purchased at fiber festival",
        client=None,
        raw_stash_items=existing_items,
    )

    assert success is True
    assert "Successfully added 'Indie Dyer Artisan Singles'" in str(msg)
    assert len(updated_stash) == 2

    new_item = updated_stash[0]
    assert new_item["name"] == "Indie Dyer Artisan Singles"
    assert new_item["colorway_name"] == "Sunset Glow"
    assert new_item["dye_lot"] == "Lot A"
    assert new_item["skeins"] == 3.0
    assert new_item["total_yards"] == 1200.0
    assert new_item["total_grams"] == 300.0
    assert new_item["total_meters"] == 1097.28
    assert new_item["location"] == "Top Shelf"
    assert new_item["notes"] == "Purchased at fiber festival"
    assert new_item["yarn"]["yarn_weight"]["name"] == "Fingering"


def test_handle_manual_add_to_stash_logic_api_success() -> None:
    """Verify create_stash_item is invoked with appropriate kwargs when client is present."""
    mock_client = MagicMock()
    mock_client.create_stash_item.return_value = {
        "id": 999,
        "name": "Local Mill Handspun Worsted",
        "colorway_name": "Autumn Woods",
        "skeins": 2.0,
        "total_yards": 400.0,
        "total_grams": 200.0,
    }

    success, msg, updated_stash = handle_manual_add_to_stash_logic(
        name="Handspun Worsted",
        brand="Local Mill",
        weight="Worsted",
        colorway="Autumn Woods",
        dyelot="101",
        skeins=2.0,
        yards=400.0,
        grams=200.0,
        location="Bin 2",
        status="In stash",
        notes="Spun on drop spindle",
        client=mock_client,
        raw_stash_items=[],
    )

    assert success is True
    mock_client.create_stash_item.assert_called_once()
    _, kwargs = mock_client.create_stash_item.call_args
    assert kwargs.get("yarn_name") == "Handspun Worsted"
    assert kwargs.get("yarn_company_name") == "Local Mill"
    assert kwargs.get("colorway_name") == "Autumn Woods"
    assert kwargs.get("skeins") == 2.0
    assert kwargs.get("total_yards") == 400.0
    assert kwargs.get("total_grams") == 200.0
    assert kwargs.get("location") == "Bin 2"
    assert kwargs.get("notes") == "Spun on drop spindle"

    assert len(updated_stash) == 1
    assert updated_stash[0]["id"] == 999


def test_manual_yarn_callbacks_registration() -> None:
    """Verify manual yarn callbacks register cleanly on Dash app instance."""
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    register_manual_yarn_callbacks(app)
    assert getattr(app, "_manual_yarn_callbacks_registered", False) is True
