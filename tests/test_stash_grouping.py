from unittest.mock import MagicMock
import dash_bootstrap_components as dbc
from dash import html
from stashies.app_controller import AppController

def test_render_stash_cards_grouping():
    # Setup controller with mocked model
    controller = AppController(header_id="h", search_id="s", result_id="r")
    controller.MODEL = MagicMock()
    
    # Mock two stash items sharing the same yarn brand and name
    mock_stash = [
        {
            "id": 1,
            "name": "Yarn A",
            "colorway_name": "Colorway 1",
            "stash_status": {"id": 1, "name": "Active"},
            "yarn": {
                "name": "Yarn A",
                "yarn_company_name": "Brand X",
            },
            "packs": [{"skeins": 2.0, "total_yards": 400.0, "total_grams": 100.0}]
        },
        {
            "id": 2,
            "name": "Yarn A",
            "colorway_name": "Colorway 2",
            "stash_status": {"id": 1, "name": "Active"},
            "yarn": {
                "name": "Yarn A",
                "yarn_company_name": "Brand X",
            },
            "packs": [{"skeins": 1.0, "total_yards": 200.0, "total_grams": 50.0}]
        }
    ]
    
    controller.MODEL.get_stash_list.return_value = mock_stash

    # Render stash cards list
    cols = controller.render_stash_cards(query=None)
    
    assert len(cols) == 1
    # Verify we got a Card (custom accordion container)
    card = cols[0].children
    assert isinstance(card, dbc.Card)
    
    header, collapse = card.children
    assert isinstance(header, html.Div)
    assert isinstance(collapse, dbc.Collapse)
    
    # Verify the collapsed body has the two colorway rows
    body = collapse.children
    assert isinstance(body, html.Div)
    # 2 colorway row elements
    assert len(body.children) == 2


def test_toggle_edit_modal_robust_matching():
    import datetime
    from dash import no_update
    
    # Setup controller with mocked model
    controller = AppController(header_id="h", search_id="s", result_id="r")
    controller.MODEL = MagicMock()
    controller.MODEL.get_stash_history.return_value = []

    # Test case 1: Cancel button triggered
    res = controller.toggle_edit_modal(
        edit_clicks=[],
        cancel_click=1,
        store_data_list=[],
        btn_ids=[],
        triggered_id="edit-stash-cancel-btn.n_clicks"
    )
    assert res[0] is False
    assert res[1] is no_update
    assert res[12] == datetime.date.today().isoformat()

    # Test case 2: Valid edit button click and match found (with numeric/string matching)
    res = controller.toggle_edit_modal(
        edit_clicks=[1],
        cancel_click=None,
        store_data_list=[
            {"id": 123, "skeins": 5.0, "name": "Soft Wool", "colorway": "Red", "dye_lot": "A", "location": "Box", "notes": "notes", "status_id": 1}
        ],
        btn_ids=[{"index": 123}],
        triggered_id='{"index": 123, "type": "edit-btn"}.n_clicks'
    )
    assert res[0] is True
    assert res[1] == 123
    assert res[2] == 5.0
    assert res[3] == "Red"
    assert res[4] == "A"
    assert res[5] == "Box"
    assert res[6] == "notes"
    assert res[7] == 5.0
    assert res[8] == 1
    assert res[13] == "edit entry: Soft Wool"

    # Test case 3: Match with mismatched types (index string vs integer ID)
    res = controller.toggle_edit_modal(
        edit_clicks=[1],
        cancel_click=None,
        store_data_list=[
            {"id": "123", "skeins": 5.0, "name": "Soft Wool", "colorway": "Red", "dye_lot": "A", "location": "Box", "notes": "notes", "status_id": 1}
        ],
        btn_ids=[{"index": 123}],
        triggered_id='{"index": 123, "type": "edit-btn"}.n_clicks'
    )
    assert res[0] is True
    assert res[1] == "123"

    # Test case 4: Triggered ID doesn't parse
    res = controller.toggle_edit_modal(
        edit_clicks=[1],
        cancel_click=None,
        store_data_list=[{"id": 123}],
        btn_ids=[{"index": 123}],
        triggered_id="invalid-json"
    )
    assert res == (no_update,) * 14

