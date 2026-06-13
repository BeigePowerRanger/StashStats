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
