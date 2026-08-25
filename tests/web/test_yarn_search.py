"""Tests for Yarn Search UI components, form inputs, accordion rendering, pagination, and layout."""

from typing import Any

import dash_bootstrap_components as dbc
from dash import html
from dash.development.base_component import Component

from stashstats.models.common import Photo
from stashstats.models.yarn import YarnSearchResult, YarnWeight
from stashstats.web.components.search import (
    SEARCH_CATEGORIES,
    SORT_CATEGORIES,
    create_yarn_search_accordion,
    create_yarn_search_accordion_item,
    create_yarn_search_details,
    create_yarn_search_form,
    create_yarn_search_pagination,
)
from stashstats.web.layouts.main import create_main_layout
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


def make_sample_yarn_search_results() -> list[YarnSearchResult]:
    """Helper to create realistic YarnSearchResult models for testing."""
    yarn1 = YarnSearchResult(
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
            small_url="https://images.ravelry.com/rios_sm.jpg",
        ),
        yarn_weight=YarnWeight(
            id=5,
            name="Worsted",
            ply="4",
            wpi="9",
            knit_gauge="18-22 sts = 4 inches",
        ),
    )

    yarn2 = YarnSearchResult(
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
    )

    yarn3 = YarnSearchResult(
        id=8888,
        name="Vintage DK Discontinued",
        permalink="vintage-dk-disc",
        yarn_company_name="Old Mills",
        grams=50.0,
        yardage=125.0,
        discontinued=True,
        machine_washable=False,
        rating_average=None,
        rating_count=0,
        first_photo=None,
        yarn_weight=None,
    )

    return [yarn1, yarn2, yarn3]


# ===========================================================================
# 1. Search Form & Input Components Tests
# ===========================================================================


def test_create_yarn_search_form_structure() -> None:
    """Verify search form renders category, query, sort, and submit button."""
    form = create_yarn_search_form(query="merino", brand="Malabrigo", category="yarns", sort="best_match")
    assert isinstance(form, (dbc.Row, dbc.Form, html.Div))

    # Category selector
    cat_input = find_component_by_id(form, "yarn-search-category-input")
    assert cat_input is not None
    assert getattr(cat_input, "value", None) == "yarns"
    assert getattr(cat_input, "options", None) == SEARCH_CATEGORIES

    # Search keyword input
    query_input = find_component_by_id(form, "yarn-search-query-input")
    assert query_input is not None
    assert getattr(query_input, "value", None) == "merino"
    assert getattr(query_input, "placeholder", None) == "Flux Capacitor"

    # Brand input
    brand_input = find_component_by_id(form, "yarn-search-brand-input")
    assert brand_input is not None
    assert getattr(brand_input, "value", None) == "Malabrigo"

    # Sort selector
    sort_input = find_component_by_id(form, "yarn-search-sort-input")
    assert sort_input is not None
    assert getattr(sort_input, "value", None) == "best_match"
    assert getattr(sort_input, "options", None) == SORT_CATEGORIES

    # Submit button
    search_btn = find_component_by_id(form, "yarn-search-btn")
    assert search_btn is not None
    json_repr = str(search_btn.to_plotly_json())
    assert "Search" in json_repr
    assert "bi-search" in json_repr


def test_create_yarn_search_form_defaults() -> None:
    """Verify search form renders default input values."""
    form = create_yarn_search_form()
    query_input = find_component_by_id(form, "yarn-search-query-input")
    brand_input = find_component_by_id(form, "yarn-search-brand-input")
    cat_input = find_component_by_id(form, "yarn-search-category-input")
    sort_input = find_component_by_id(form, "yarn-search-sort-input")

    assert getattr(query_input, "value", None) == ""
    assert getattr(brand_input, "value", None) == ""
    assert getattr(cat_input, "value", None) == "yarns"
    assert getattr(sort_input, "value", None) == "best_match"


# ===========================================================================
# 2. Accordion Item & Details Component Tests
# ===========================================================================


def test_create_yarn_search_accordion_item_with_photo_and_specs() -> None:
    """Verify accordion card header and details render correctly for full yarn spec."""
    yarns = make_sample_yarn_search_results()
    yarn = yarns[0]  # Rios

    item = create_yarn_search_accordion_item(yarn, index=0)
    assert isinstance(item, dbc.AccordionItem)

    json_repr = str(item.to_plotly_json())

    # Header elements
    assert "Rios" in json_repr
    assert "Malabrigo" in json_repr
    assert "https://images.ravelry.com/rios_sq.jpg" in json_repr

    # Body details
    assert "210" in json_repr  # Yardage
    assert "100" in json_repr  # Grams
    assert "4.8" in json_repr or "4.75" in json_repr  # Rating
    assert "plied" in json_repr  # Texture
    assert "malabrigo-yarn-rios" in json_repr  # Permalink / Link
    assert "Add to Stash" in json_repr  # Inline stash form


def test_create_yarn_search_accordion_item_discontinued_and_fallback_photo() -> None:
    """Verify discontinued badge and fallback icon render when data is minimal."""
    yarns = make_sample_yarn_search_results()
    yarn = yarns[2]  # Discontinued yarn with no photo and no weight

    item = create_yarn_search_accordion_item(yarn, index=2)
    assert isinstance(item, dbc.AccordionItem)

    json_repr = str(item.to_plotly_json())
    assert "Vintage DK Discontinued" in json_repr
    assert "Old Mills" in json_repr
    assert "Discontinued" in json_repr
    # Check fallback icon
    assert "bi-box-seam" in json_repr or "bi-image" in json_repr or "bi-camera" in json_repr


def test_create_yarn_search_accordion_item_from_dict() -> None:
    """Verify create_yarn_search_accordion_item accepts dictionary payload."""
    yarns = make_sample_yarn_search_results()
    yarn_dict = yarns[1].model_dump()

    item = create_yarn_search_accordion_item(yarn_dict, index=1)
    assert isinstance(item, dbc.AccordionItem)
    json_repr = str(item.to_plotly_json())
    assert "220 Superwash" in json_repr
    assert "Cascade Yarns" in json_repr


def test_create_yarn_search_details_structure() -> None:
    """Verify create_yarn_search_details produces structured specs and stash form."""
    yarns = make_sample_yarn_search_results()
    details = create_yarn_search_details(yarns[0])
    assert isinstance(details, html.Div)
    json_repr = str(details.to_plotly_json())

    assert "Weight:" in json_repr or "Worsted" in json_repr
    assert "Yardage:" in json_repr or "210" in json_repr
    assert "Grams:" in json_repr or "100" in json_repr
    assert "Machine Washable" in json_repr or "Washable" in json_repr
    assert "Ravelry" in json_repr
    assert "Add to Stash" in json_repr


def test_create_yarn_search_details_with_colorways_prefilled_and_manual_input() -> None:
    """Verify colorways are pre-filled in API dropdown and manual input is available."""
    yarn_with_cws = {
        "id": 999,
        "name": "Malabrigo Rios",
        "yarn_company_name": "Malabrigo",
        "colorways": ["Diana", "Frank Ochre", "Peacock"],
        "yardage": 210.0,
        "grams": 100.0,
    }
    details = create_yarn_search_details(yarn_with_cws)
    json_repr = str(details.to_plotly_json())

    # Official colorways in Select
    assert "Colorway (API)" in json_repr
    assert "Diana" in json_repr
    assert "Frank Ochre" in json_repr
    assert "Peacock" in json_repr

    # Custom / Manual Colorway Input
    assert "Custom Colorway" in json_repr
    assert "stash-colorway-manual" in json_repr


# ===========================================================================
# 3. Accordion List & Empty State Tests
# ===========================================================================


def test_create_yarn_search_accordion_populated() -> None:
    """Verify accordion renders multiple AccordionItem children for results list."""
    yarns = make_sample_yarn_search_results()
    accordion = create_yarn_search_accordion(yarns)

    assert isinstance(accordion, dbc.Accordion)
    assert getattr(accordion, "id", None) == "yarn-search-accordion"
    assert len(accordion.children) == 3


def test_create_yarn_search_accordion_empty() -> None:
    """Verify empty list renders empty state alert/placeholder."""
    empty_elem = create_yarn_search_accordion([])
    empty_state = find_component_by_id(empty_elem, "yarn-search-empty-state")
    assert empty_state is not None
    json_repr = str(empty_state.to_plotly_json())
    assert "No yarns found" in json_repr or "search" in json_repr.lower()


def test_create_yarn_search_accordion_none() -> None:
    """Verify None input renders initial / empty state."""
    empty_elem = create_yarn_search_accordion(None)
    empty_state = find_component_by_id(empty_elem, "yarn-search-empty-state")
    assert empty_state is not None


# ===========================================================================
# 4. Pagination Component Tests
# ===========================================================================


def test_create_yarn_search_pagination_structure() -> None:
    """Verify pagination renders dbc.Pagination component and pagination info text."""
    pag_elem = create_yarn_search_pagination(page=2, total_pages=5, total_results=245)

    pagination = find_component_by_id(pag_elem, "yarn-search-pagination")
    assert pagination is not None
    assert getattr(pagination, "active_page", None) == 2
    assert getattr(pagination, "max_value", None) == 5

    info = find_component_by_id(pag_elem, "yarn-search-pagination-info")
    assert info is not None
    json_repr = str(info.to_plotly_json())
    assert "Showing page 2 of 5" in json_repr
    assert "245 yarns" in json_repr or "245" in json_repr


def test_create_yarn_search_pagination_single_page() -> None:
    """Verify pagination with single page clamps max_value to at least 1."""
    pag_elem = create_yarn_search_pagination(page=1, total_pages=1, total_results=3)
    pagination = find_component_by_id(pag_elem, "yarn-search-pagination")
    assert pagination is not None
    assert getattr(pagination, "max_value", None) == 1


# ===========================================================================
# 5. Full Search Layout Tests
# ===========================================================================


def test_create_yarn_search_layout_structure() -> None:
    """Verify search layout contains form, accordion container, pagination, and stores."""
    yarns = make_sample_yarn_search_results()
    layout = create_yarn_search_layout(
        yarns=yarns,
        page=1,
        total_pages=3,
        total_results=75,
        query="merino",
        brand="Malabrigo",
    )

    assert getattr(layout, "id", None) == "yarn-search-container"

    # Search form inputs
    assert find_component_by_id(layout, "yarn-search-category-input") is not None
    assert find_component_by_id(layout, "yarn-search-query-input") is not None
    assert find_component_by_id(layout, "yarn-search-sort-input") is not None
    assert find_component_by_id(layout, "yarn-search-btn") is not None

    # Results container wrapped in spinner
    assert find_component_by_id(layout, "yarn-search-list-container") is not None
    assert find_component_by_id(layout, "yarn-search-accordion") is not None

    spinner = next((c for c in layout.children if isinstance(c, dbc.Spinner)), None)
    assert spinner is not None
    assert getattr(spinner, "color", None) == "primary"
    assert getattr(spinner, "type", None) == "border"

    # Pagination container
    assert find_component_by_id(layout, "yarn-search-pagination") is not None
    assert find_component_by_id(layout, "yarn-search-pagination-info") is not None

    # Data stores
    assert find_component_by_id(layout, "yarn-search-results-store") is not None
    assert find_component_by_id(layout, "yarn-search-paginator-store") is not None


def test_create_yarn_search_layout_default_empty() -> None:
    """Verify default search layout starts with empty search state."""
    layout = create_yarn_search_layout()
    assert getattr(layout, "id", None) == "yarn-search-container"
    assert find_component_by_id(layout, "yarn-search-empty-state") is not None


# ===========================================================================
# 6. Main Navigation Tab Integration Tests
# ===========================================================================


def test_main_layout_yarn_search_tab_integration() -> None:
    """Verify create_main_layout with active_tab='tab-search' renders yarn search layout."""
    layout = create_main_layout(active_tab="tab-search")

    tabs = find_component_by_id(layout, "main-tabs")
    assert tabs is not None
    assert getattr(tabs, "value", None) == "tab-search"

    tab_content = find_component_by_id(layout, "tab-content")
    assert tab_content is not None

    # Check that yarn-search-container is rendered in tab-content
    search_container = find_component_by_id(tab_content, "yarn-search-container")
    assert search_container is not None
    assert find_component_by_id(search_container, "yarn-search-query-input") is not None
    assert find_component_by_id(search_container, "yarn-search-btn") is not None
