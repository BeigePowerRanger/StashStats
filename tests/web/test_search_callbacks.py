"""Tests for Yarn Search reactive callbacks, pagination handling, and RavelryClient integration."""

from typing import Any
from unittest.mock import MagicMock

import dash
import dash_bootstrap_components as dbc
import pytest
from dash.development.base_component import Component

from stashstats.exceptions import RavelryAPIError
from stashstats.models.common import Paginator, Photo
from stashstats.models.yarn import YarnSearchResponse, YarnSearchResult, YarnWeight
from stashstats.web.app import create_app
from stashstats.web.callbacks.search import (
    build_search_query,
    handle_add_to_stash_logic,
    handle_yarn_search_callback,
    register_search_callbacks,
    update_yarn_search_logic,
)
from stashstats.web.layouts.search import create_yarn_search_layout


def find_component_by_id(tree: Any, component_id: Any) -> Component | None:
    """Recursively search Dash component tree by component id."""
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


def make_mock_yarn_results() -> list[YarnSearchResult]:
    """Create sample YarnSearchResult items for callback testing."""
    return [
        YarnSearchResult(
            id=2420,
            name="Rios",
            permalink="malabrigo-yarn-rios",
            yarn_company_name="Malabrigo",
            grams=100.0,
            yardage=210.0,
            discontinued=False,
            machine_washable=True,
            texture="plied",
            wpi=9,
            min_gauge=18.0,
            max_gauge=22.0,
            gauge_divisor=4,
            rating_average=4.75,
            rating_count=15420,
            first_photo=Photo(
                id=12345,
                square_url="https://images.ravelry.com/rios_sq.jpg",
            ),
            yarn_weight=YarnWeight(
                id=5,
                name="Worsted",
            ),
        ),
        YarnSearchResult(
            id=500,
            name="220 Superwash",
            permalink="cascade-yarns-220-superwash",
            yarn_company_name="Cascade Yarns",
            grams=100.0,
            yardage=220.0,
            discontinued=False,
            machine_washable=True,
            texture="plied",
            rating_average=4.42,
            rating_count=8900,
            first_photo=None,
            yarn_weight=YarnWeight(
                id=5,
                name="Worsted",
            ),
        ),
    ]


# ===========================================================================
# 1. Query Builder Tests
# ===========================================================================


def test_build_search_query_query_only() -> None:
    """Verify build_search_query with keyword only."""
    assert build_search_query("merino", None) == "merino"
    assert build_search_query("  merino wool  ", "") == "merino wool"


def test_build_search_query_brand_only() -> None:
    """Verify build_search_query with brand only."""
    assert build_search_query(None, "Malabrigo") == "Malabrigo"
    assert build_search_query("", "  Cascade Yarns  ") == "Cascade Yarns"


def test_build_search_query_both() -> None:
    """Verify build_search_query combines brand and keyword."""
    query = build_search_query("Rios", "Malabrigo")
    assert query == "Malabrigo Rios"

    query_padded = build_search_query("  worsted wool ", " Cascade ")
    assert query_padded == "Cascade worsted wool"


def test_build_search_query_empty() -> None:
    """Verify build_search_query handles None and empty strings."""
    assert build_search_query(None, None) == ""
    assert build_search_query("", "") == ""
    assert build_search_query("   ", "   ") == ""


# ===========================================================================
# 2. update_yarn_search_logic Tests
# ===========================================================================


def test_update_yarn_search_logic_success() -> None:
    """Verify successful API search returns populated accordion, page metrics, and store data."""
    mock_client = MagicMock()
    sample_yarns = make_mock_yarn_results()
    mock_response = YarnSearchResponse(
        paginator=Paginator(
            page=1,
            page_size=25,
            page_count=3,
            last_page=3,
            results=75,
        ),
        yarns=sample_yarns,
    )
    mock_client.search_yarns.return_value = mock_response

    accordion, total_pages, page, info, results_store, paginator_store = update_yarn_search_logic(
        client=mock_client,
        query="Rios",
        brand="Malabrigo",
        active_page=1,
        page_size=25,
    )

    mock_client.search_yarns.assert_called_once_with(
        query="Malabrigo Rios",
        page=1,
        page_size=25,
        sort="best",
    )

    assert total_pages == 3
    assert page == 1
    assert "Showing page 1 of 3 (75 yarns found)" in info
    assert isinstance(accordion, dbc.Accordion)
    assert len(results_store) == 2
    assert results_store[0]["name"] == "Rios"
    assert paginator_store == {
        "page": 1,
        "total_pages": 3,
        "total_results": 75,
        "query": "Rios",
        "brand": "Malabrigo",
        "sort": "best_match",
    }


def test_update_yarn_search_logic_pagination() -> None:
    """Verify requesting page 2 passes page=2 to API client and clamps correctly."""
    mock_client = MagicMock()
    sample_yarns = make_mock_yarn_results()
    mock_response = YarnSearchResponse(
        paginator=Paginator(
            page=2,
            page_size=25,
            page_count=5,
            last_page=5,
            results=120,
        ),
        yarns=sample_yarns,
    )
    mock_client.search_yarns.return_value = mock_response

    accordion, total_pages, page, info, results_store, paginator_store = update_yarn_search_logic(
        client=mock_client,
        query="wool",
        brand=None,
        active_page=2,
        page_size=25,
    )

    mock_client.search_yarns.assert_called_once_with(
        query="wool",
        page=2,
        page_size=25,
        sort="best",
    )

    assert total_pages == 5
    assert page == 2
    assert "Showing page 2 of 5 (120 yarns found)" in info
    assert paginator_store["page"] == 2
    assert isinstance(accordion, dbc.Accordion)
    assert len(results_store) == 2


def test_update_yarn_search_logic_empty_results() -> None:
    """Verify empty search results render empty state alert."""
    mock_client = MagicMock()
    mock_response = YarnSearchResponse(
        paginator=Paginator(
            page=1,
            page_size=25,
            page_count=1,
            last_page=1,
            results=0,
        ),
        yarns=[],
    )
    mock_client.search_yarns.return_value = mock_response

    accordion, total_pages, page, info, results_store, paginator_store = update_yarn_search_logic(
        client=mock_client,
        query="NonExistentYarn9999",
        brand=None,
        active_page=1,
    )

    assert total_pages == 1
    assert page == 1
    assert "0 yarns found" in info
    assert results_store == []
    assert paginator_store["total_results"] == 0
    empty_elem = find_component_by_id(accordion, "yarn-search-empty-state")
    assert empty_elem is not None


def test_update_yarn_search_logic_no_client() -> None:
    """Verify update_yarn_search_logic handles client=None by returning warning alert."""
    accordion, total_pages, page, info, results_store, paginator_store = update_yarn_search_logic(
        client=None,
        query="merino",
        brand=None,
        active_page=1,
    )

    assert total_pages == 1
    assert page == 1
    assert "missing in .env" in info or "credentials" in info.lower()
    assert results_store == []
    assert paginator_store["total_results"] == 0
    warning_elem = find_component_by_id(accordion, "yarn-search-warning-state")
    assert warning_elem is not None
    json_repr = str(warning_elem.to_plotly_json())
    assert "warning" in json_repr
    assert ".env" in json_repr


def test_update_yarn_search_logic_empty_inputs() -> None:
    """Verify update_yarn_search_logic with empty inputs returns informative info text."""
    mock_client = MagicMock()
    accordion, total_pages, page, info, results_store, _paginator_store = update_yarn_search_logic(
        client=mock_client,
        query="",
        brand="",
        active_page=1,
    )

    mock_client.search_yarns.assert_not_called()
    assert total_pages == 1
    assert page == 1
    assert info == "Enter a keyword or brand to search yarns."
    assert results_store == []
    assert find_component_by_id(accordion, "yarn-search-empty-state") is not None


def test_update_yarn_search_logic_api_error() -> None:
    """Verify API error is caught and rendered as error state."""
    mock_client = MagicMock()
    mock_client.search_yarns.side_effect = RavelryAPIError("Ravelry API down 503")

    accordion, total_pages, page, info, results_store, _paginator_store = update_yarn_search_logic(
        client=mock_client,
        query="merino",
        brand=None,
        active_page=1,
    )

    assert total_pages == 1
    assert page == 1
    assert "Search error" in info or "Error" in info
    assert results_store == []
    error_state = find_component_by_id(accordion, "yarn-search-error-state")
    assert error_state is not None
    assert "503" in str(error_state.to_plotly_json())


# ===========================================================================
# 3. handle_yarn_search_callback Trigger Dispatch Tests
# ===========================================================================


def test_handle_yarn_search_callback_search_btn_trigger() -> None:
    """Verify search button trigger resets page to 1 and searches newly entered inputs."""
    mock_client = MagicMock()
    mock_client.search_yarns.return_value = YarnSearchResponse(
        paginator=Paginator(page=1, page_size=25, page_count=2, last_page=2, results=50),
        yarns=make_mock_yarn_results(),
    )

    res = handle_yarn_search_callback(
        client=mock_client,
        triggered_id="yarn-search-btn",
        n_clicks=1,
        query_submit=None,
        brand_submit=None,
        sort_val="highest_rating",
        active_page=5,  # Old pagination state should be ignored on new search click
        query_val="Worsted",
        brand_val="Cascade",
        paginator_store={"page": 5, "query": "old", "brand": "old", "sort": "best_match"},
    )

    accordion, total_pages, page, info, results_store, paginator_store = res
    mock_client.search_yarns.assert_called_once_with(
        query="Cascade Worsted",
        page=1,
        page_size=25,
        sort="rating",
    )
    assert page == 1
    assert total_pages == 2
    assert "Showing page 1 of 2" in info
    assert isinstance(accordion, dbc.Accordion)
    assert len(results_store) == 2
    assert paginator_store["query"] == "Worsted"


def test_handle_yarn_search_callback_enter_submit_trigger() -> None:
    """Verify Enter keypress (n_submit) on search inputs triggers search at page 1."""
    mock_client = MagicMock()
    mock_client.search_yarns.return_value = YarnSearchResponse(
        paginator=Paginator(page=1, page_size=25, page_count=1, last_page=1, results=2),
        yarns=make_mock_yarn_results(),
    )

    res = handle_yarn_search_callback(
        client=mock_client,
        triggered_id="yarn-search-query-input",
        n_clicks=None,
        query_submit=1,
        brand_submit=None,
        sort_val=None,
        active_page=1,
        query_val="Rios",
        brand_val="",
        paginator_store=None,
    )

    accordion, _total_pages, page, _info, _results_store, _paginator_store = res
    mock_client.search_yarns.assert_called_once_with(
        query="Rios",
        page=1,
        page_size=25,
        sort="best",
    )
    assert page == 1
    assert isinstance(accordion, dbc.Accordion)


def test_handle_yarn_search_callback_pagination_trigger() -> None:
    """Verify pagination click preserves active query and fetches requested page."""
    mock_client = MagicMock()
    mock_client.search_yarns.return_value = YarnSearchResponse(
        paginator=Paginator(page=3, page_size=25, page_count=4, last_page=4, results=90),
        yarns=make_mock_yarn_results(),
    )

    res = handle_yarn_search_callback(
        client=mock_client,
        triggered_id="yarn-search-pagination",
        n_clicks=1,
        query_submit=None,
        brand_submit=None,
        sort_val=None,
        active_page=3,
        query_val="typing new query",  # User typed something else but clicked page 3 of current results
        brand_val="",
        paginator_store={"page": 2, "total_pages": 4, "query": "merino", "brand": "Malabrigo", "sort": "most_projects"},
    )

    accordion, _total_pages, page, _info, _results_store, _paginator_store = res
    mock_client.search_yarns.assert_called_once_with(
        query="Malabrigo merino",
        page=3,
        page_size=25,
        sort="projects",
    )
    assert page == 3
    assert isinstance(accordion, dbc.Accordion)


def test_handle_yarn_search_callback_prevent_update_on_no_trigger() -> None:
    """Verify PreventUpdate is raised when no user action has occurred."""
    with pytest.raises(dash.exceptions.PreventUpdate):
        handle_yarn_search_callback(
            client=None,
            triggered_id=None,
            n_clicks=None,
            query_submit=None,
            brand_submit=None,
            sort_val=None,
            active_page=None,
            query_val=None,
            brand_val=None,
            paginator_store=None,
        )


# ===========================================================================
# 4. Callback Registration & App Factory Tests
# ===========================================================================


def test_register_search_callbacks() -> None:
    """Verify register_search_callbacks attaches callbacks to Dash app."""
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    app.layout = create_yarn_search_layout()

    register_search_callbacks(app)
    assert getattr(app, "_search_callbacks_registered", False) is True

    # Call again to verify idempotency
    register_search_callbacks(app)
    assert getattr(app, "_search_callbacks_registered", False) is True


def test_create_app_registers_search_callbacks() -> None:
    """Verify create_app registers search callbacks."""
    app = create_app()
    outputs = list(app.callback_map.keys())

    # Check search callback outputs in map
    assert any("yarn-search-list-container" in o for o in outputs)
    assert any("yarn-search-pagination" in o for o in outputs)
    assert any("yarn-search-pagination-info" in o for o in outputs)
    assert any("yarn-search-results-store" in o for o in outputs)
    assert any("yarn-search-paginator-store" in o for o in outputs)


# ===========================================================================
# 5. handle_add_to_stash_logic Tests
# ===========================================================================


def test_handle_add_to_stash_logic_with_client() -> None:
    """Verify handle_add_to_stash_logic calls client.create_stash_item and updates raw_stash store."""
    from stashstats.models.stash import StashItem

    mock_client = MagicMock()
    mock_item = StashItem(
        id=777,
        name="Malabrigo Rios - Diana",
        permalink="malabrigo-rios-diana",
        colorway_name="Diana",
        skeins=2.0,
        total_yards=420.0,
        total_grams=200.0,
    )
    mock_client.create_stash_item.return_value = mock_item

    sample_search_results = [
        {"id": 2420, "name": "Rios", "yarn_company_name": "Malabrigo", "grams": 100.0, "yardage": 210.0}
    ]
    raw_stash_items = [{"id": 1, "name": "Cascade 220", "skeins": 3.0}]

    status_msg, updated_stash = handle_add_to_stash_logic(
        client=mock_client,
        yarn_id=2420,
        skeins=2.0,
        colorway="Diana",
        dyelot="42",
        location="Bin 1",
        notes="Knitting sweater",
        date_added="2026-08-24",
        search_results=sample_search_results,
        raw_stash_items=raw_stash_items,
    )

    mock_client.create_stash_item.assert_called_once()
    _, kwargs = mock_client.create_stash_item.call_args
    assert kwargs.get("yarn_id") == 2420
    assert kwargs.get("colorway_name") == "Diana"
    assert kwargs.get("skeins") == 2.0

    assert "Successfully added" in status_msg
    assert len(updated_stash) == 2
    assert updated_stash[0]["id"] == 777
    assert updated_stash[0]["skeins"] == 2.0


def test_handle_add_to_stash_logic_offline_fallback() -> None:
    """Verify handle_add_to_stash_logic creates a synthesized stash item when client is None."""
    sample_search_results = [
        {"id": 2420, "name": "Rios", "yarn_company_name": "Malabrigo", "grams": 100.0, "yardage": 210.0, "permalink": "rios"}
    ]
    raw_stash_items = []

    status_msg, updated_stash = handle_add_to_stash_logic(
        client=None,
        yarn_id=2420,
        skeins=3.0,
        colorway="Diana",
        dyelot="42",
        location="Bin 1",
        notes="Sample notes",
        date_added="2026-08-24",
        search_results=sample_search_results,
        raw_stash_items=raw_stash_items,
    )

    assert "Successfully added" in status_msg
    assert len(updated_stash) == 1
    new_item = updated_stash[0]
    assert new_item["name"] == "Malabrigo Rios"
    assert new_item["skeins"] == 3.0
    assert new_item["total_yards"] == 630.0
    assert new_item["total_grams"] == 300.0
    assert new_item["colorway_name"] == "Diana"
    assert new_item["stash_status"]["name"] == "In stash"


def test_handle_yarn_search_callback_empty_query_search_btn() -> None:
    """Verify clicking search button with empty query searches all popular yarns."""
    mock_client = MagicMock()
    mock_client.search_yarns.return_value = YarnSearchResponse(
        paginator=Paginator(page=1, page_size=25, page_count=10, last_page=10, results=250),
        yarns=make_mock_yarn_results(),
    )

    res = handle_yarn_search_callback(
        client=mock_client,
        triggered_id="yarn-search-btn",
        n_clicks=1,
        query_submit=None,
        brand_submit=None,
        sort_val=None,
        active_page=1,
        query_val="",
        brand_val="",
        paginator_store=None,
    )

    accordion, total_pages, page, info, results_store, _ = res
    mock_client.search_yarns.assert_called_once_with(
        query="",
        page=1,
        page_size=25,
        sort="best",
    )
    assert page == 1
    assert total_pages == 10
    assert "Showing page 1 of 10" in info
    assert len(results_store) == 2

