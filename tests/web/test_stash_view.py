"""Tests for Personal Stash view: grouping engine, sorting, filtering, components, layout, and callbacks."""

from typing import Any
from unittest.mock import MagicMock

import dash
import dash_bootstrap_components as dbc
import pytest
from dash.development.base_component import Component

from stashstats.models.stash import Pack, StashItem, StashStatus, StashYarn
from stashstats.models.yarn import YarnWeight
from stashstats.web.callbacks.stash import (
    handle_stash_sync_logic,
    register_stash_callbacks,
    update_stash_view_logic,
)
from stashstats.web.components.stash import (
    ParentYarnGroup,
    create_grouped_stash_accordion,
    create_parent_yarn_accordion_item,
    create_stash_item_row,
    filter_stash_groups,
    group_stash_items,
    paginate_stash_groups,
    sort_stash_groups,
)
from stashstats.web.layouts.stash import create_stash_layout


def find_component_by_id(tree: Any, component_id: str | dict) -> Component | None:
    """Recursively find a Dash component by its id (string or dict)."""
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


def make_sample_stash_items() -> list[StashItem]:
    """Helper to create a diverse list of sample StashItem models for testing."""
    item1 = StashItem(
        id=101,
        name="Malabrigo Rios Diana",
        permalink="item-101",
        colorway_name="Diana",
        dye_lot="42",
        location="Box 3",
        created_at="2026-02-10 10:00:00",
        tag_names=["sweater-qty"],
        stash_status=StashStatus(id=1, name="In stash"),
        yarn=StashYarn(
            id=2420,
            name="Rios",
            yarn_company_name="Malabrigo",
            yarn_weight=YarnWeight(id=5, name="Worsted"),
        ),
        primary_pack=Pack(
            id=1,
            colorway="Diana",
            dye_lot="42",
            skeins=3.0,
            total_yards=630.0,
            total_meters=576.0,
            total_grams=300.0,
            purchased_date="2026-02-10",
        ),
        packs=[
            Pack(
                id=1,
                colorway="Diana",
                dye_lot="42",
                skeins=3.0,
                total_yards=630.0,
                total_meters=576.0,
                total_grams=300.0,
            )
        ],
    )

    item2 = StashItem(
        id=102,
        name="Malabrigo Rios Frank Ochre",
        permalink="item-102",
        colorway_name="Frank Ochre",
        dye_lot="99",
        location="Shelf 1",
        created_at="2026-03-01 12:00:00",
        stash_status=StashStatus(id=1, name="In stash"),
        yarn=StashYarn(
            id=2420,
            name="Rios",
            yarn_company_name="Malabrigo",
            yarn_weight=YarnWeight(id=5, name="Worsted"),
        ),
        primary_pack=Pack(
            id=2,
            colorway="Frank Ochre",
            dye_lot="99",
            skeins=1.5,
            total_yards=315.0,
            total_meters=288.0,
            total_grams=150.0,
            purchased_date="2026-03-01",
        ),
        packs=[
            Pack(
                id=2,
                colorway="Frank Ochre",
                dye_lot="99",
                skeins=1.5,
                total_yards=315.0,
                total_meters=288.0,
                total_grams=150.0,
            )
        ],
    )

    item3 = StashItem(
        id=103,
        name="Cascade 220 Navy",
        permalink="item-103",
        colorway_name="Navy",
        dye_lot="100",
        location="Bin A",
        created_at="2026-01-15 08:00:00",
        stash_status=StashStatus(id=2, name="Used up"),
        yarn=StashYarn(
            id=500,
            name="220 Superwash",
            yarn_company_name="Cascade Yarns",
            yarn_weight=YarnWeight(id=5, name="Worsted"),
        ),
        primary_pack=Pack(
            id=3,
            colorway="Navy",
            dye_lot="100",
            skeins=2.0,
            total_yards=440.0,
            total_meters=400.0,
            total_grams=200.0,
            purchased_date="2026-01-15",
        ),
        packs=[
            Pack(
                id=3,
                colorway="Navy",
                skeins=2.0,
                total_yards=440.0,
                total_meters=400.0,
                total_grams=200.0,
            )
        ],
    )

    item4 = StashItem(
        id=104,
        name="Handspun Merino Braid",
        permalink="item-104",
        colorway_name="Sunset",
        location="Stash Bag 4",
        created_at="2026-04-10 15:00:00",
        stash_status=StashStatus(id=1, name="In stash"),
        yarn=None,  # Unlinked yarn
        primary_pack=Pack(
            id=4,
            colorway="Sunset",
            skeins=1.0,
            total_yards=200.0,
            total_meters=182.0,
            total_grams=100.0,
        ),
    )

    return [item1, item2, item3, item4]


# ---------------------------------------------------------------------------
# 1. Grouping Engine Tests
# ---------------------------------------------------------------------------


def test_group_stash_items_by_parent_yarn() -> None:
    """Verify items are correctly grouped by parent yarn brand and product name."""
    items = make_sample_stash_items()
    groups = group_stash_items(items)

    # 4 items: 2 Malabrigo Rios, 1 Cascade 220, 1 Handspun
    assert len(groups) == 3

    # Check Malabrigo group aggregation
    malabrigo_group = next(g for g in groups if "Malabrigo" in g.brand_name)
    assert malabrigo_group.yarn_name == "Rios"
    assert malabrigo_group.display_title == "Malabrigo — Rios"
    assert malabrigo_group.total_items == 2
    assert malabrigo_group.total_skeins == 4.5
    assert malabrigo_group.total_yards == 945.0
    assert malabrigo_group.total_meters == 864.0
    assert malabrigo_group.total_grams == 450.0
    assert len(malabrigo_group.items) == 2


def test_group_stash_items_unlinked_yarn() -> None:
    """Verify unlinked yarn items without yarn object form a valid group."""
    items = make_sample_stash_items()
    groups = group_stash_items(items)

    unlinked_group = next(g for g in groups if g.yarn_name == "Handspun Merino Braid")
    assert unlinked_group.brand_name == "Custom / Unlinked"
    assert unlinked_group.total_items == 1
    assert unlinked_group.total_skeins == 1.0


def test_group_stash_items_empty() -> None:
    """Verify grouping empty list returns empty list."""
    assert group_stash_items([]) == []


# ---------------------------------------------------------------------------
# 2. Filtering Tests
# ---------------------------------------------------------------------------


def test_filter_stash_groups_by_brand() -> None:
    """Verify filtering by brand name matches parent yarn."""
    groups = group_stash_items(make_sample_stash_items())

    filtered = filter_stash_groups(groups, "Malabrigo")
    assert len(filtered) == 1
    assert filtered[0].brand_name == "Malabrigo"


def test_filter_stash_groups_by_yarn_name() -> None:
    """Verify filtering by product name matches parent yarn."""
    groups = group_stash_items(make_sample_stash_items())

    filtered = filter_stash_groups(groups, "Superwash")
    assert len(filtered) == 1
    assert "Cascade" in filtered[0].brand_name


def test_filter_stash_groups_by_colorway() -> None:
    """Verify filtering matches inner colorway across items in the group."""
    groups = group_stash_items(make_sample_stash_items())

    # Diana is in Malabrigo Rios
    filtered = filter_stash_groups(groups, "Diana")
    assert len(filtered) == 1
    assert filtered[0].brand_name == "Malabrigo"


def test_filter_stash_groups_case_insensitive() -> None:
    """Verify filtering is case-insensitive and trims whitespace."""
    groups = group_stash_items(make_sample_stash_items())

    filtered = filter_stash_groups(groups, "  mAlAbRiGo  ")
    assert len(filtered) == 1


def test_filter_stash_groups_empty_query() -> None:
    """Verify None or empty query returns all groups unchanged."""
    groups = group_stash_items(make_sample_stash_items())

    assert len(filter_stash_groups(groups, None)) == len(groups)
    assert len(filter_stash_groups(groups, "")) == len(groups)
    assert len(filter_stash_groups(groups, "   ")) == len(groups)


def test_filter_stash_groups_no_matches() -> None:
    """Verify query with no matches returns empty list."""
    groups = group_stash_items(make_sample_stash_items())
    assert filter_stash_groups(groups, "NonExistentYarnPattern12345") == []


# ---------------------------------------------------------------------------
# 3. Sorting Tests
# ---------------------------------------------------------------------------


def test_sort_stash_groups_brand_asc() -> None:
    """Verify sorting by brand name ascending (A-Z)."""
    groups = group_stash_items(make_sample_stash_items())
    sorted_groups = sort_stash_groups(groups, "brand_asc")

    brands = [g.brand_name for g in sorted_groups]
    assert brands == ["Cascade Yarns", "Custom / Unlinked", "Malabrigo"]


def test_sort_stash_groups_name_asc() -> None:
    """Verify sorting by yarn product name ascending (A-Z)."""
    groups = group_stash_items(make_sample_stash_items())
    sorted_groups = sort_stash_groups(groups, "name_asc")

    yarn_names = [g.yarn_name for g in sorted_groups]
    assert yarn_names == ["220 Superwash", "Handspun Merino Braid", "Rios"]


def test_sort_stash_groups_qty_desc() -> None:
    """Verify sorting by total skeins descending (High-Low)."""
    groups = group_stash_items(make_sample_stash_items())
    sorted_groups = sort_stash_groups(groups, "qty_desc")

    skein_counts = [g.total_skeins for g in sorted_groups]
    assert skein_counts == [4.5, 2.0, 1.0]


def test_sort_stash_groups_date_desc() -> None:
    """Verify sorting by latest stash addition date descending."""
    groups = group_stash_items(make_sample_stash_items())
    sorted_groups = sort_stash_groups(groups, "date_desc")

    # Handspun is 2026-04-10, Malabrigo latest is 2026-03-01, Cascade is 2026-01-15
    titles = [g.yarn_name for g in sorted_groups]
    assert titles == ["Handspun Merino Braid", "Rios", "220 Superwash"]


# ---------------------------------------------------------------------------
# 4. Pagination Tests
# ---------------------------------------------------------------------------


def test_paginate_stash_groups() -> None:
    """Verify pagination slices groups and calculates total pages."""
    # Create 25 dummy groups
    dummy_groups = [
        ParentYarnGroup(
            brand_name=f"Brand {i:02d}",
            yarn_name=f"Yarn {i:02d}",
            display_title=f"Brand {i:02d} — Yarn {i:02d}",
            items=[],
            total_items=1,
            total_skeins=1.0,
            group_key=f"group-{i}",
        )
        for i in range(25)
    ]

    # Page 1 (10 items)
    p1_items, total_pages = paginate_stash_groups(dummy_groups, page=1, page_size=10)
    assert len(p1_items) == 10
    assert total_pages == 3
    assert p1_items[0].brand_name == "Brand 00"

    # Page 2 (10 items)
    p2_items, total_pages = paginate_stash_groups(dummy_groups, page=2, page_size=10)
    assert len(p2_items) == 10
    assert p2_items[0].brand_name == "Brand 10"

    # Page 3 (5 items)
    p3_items, total_pages = paginate_stash_groups(dummy_groups, page=3, page_size=10)
    assert len(p3_items) == 5
    assert p3_items[-1].brand_name == "Brand 24"

    # Empty list
    empty_items, total_pages = paginate_stash_groups([], page=1, page_size=10)
    assert empty_items == []
    assert total_pages == 1


# ---------------------------------------------------------------------------
# 5. UI Component Tests
# ---------------------------------------------------------------------------


def test_create_stash_item_row_structure() -> None:
    """Verify single stash item row renders colorway, dye lot, location, qty, and edit button."""
    items = make_sample_stash_items()
    item = items[0]  # Malabrigo Rios Diana

    row = create_stash_item_row(item)
    json_repr = str(row.to_plotly_json())

    assert "Diana" in json_repr
    assert "42" in json_repr  # Dye lot
    assert "Box 3" in json_repr  # Location
    assert "3 sk" in json_repr or "3.0 sk" in json_repr
    assert "630 yds" in json_repr
    assert "In stash" in json_repr

    # Verify Edit button pattern-matching ID
    edit_btn = find_component_by_id(row, {"type": "stash-edit-btn", "index": item.id})
    assert edit_btn is not None


def test_create_stash_item_row_with_pending_badge() -> None:
    """Verify dirty/pending item renders Pending Sync badge."""
    items = make_sample_stash_items()
    item = items[0]

    row = create_stash_item_row(item, is_dirty=True)
    json_repr = str(row.to_plotly_json())
    assert "Pending Sync" in json_repr


def test_create_parent_yarn_accordion_item() -> None:
    """Verify accordion card header renders thumbnail, title, aggregate badge, and body rows."""
    groups = group_stash_items(make_sample_stash_items())
    malabrigo_group = next(g for g in groups if "Malabrigo" in g.brand_name)

    accordion_item = create_parent_yarn_accordion_item(malabrigo_group, index=0)
    assert isinstance(accordion_item, dbc.AccordionItem)

    json_repr = str(accordion_item.to_plotly_json())
    assert "Malabrigo — Rios" in json_repr
    assert "2 items | 4.5 sk | 945 yds" in json_repr


def test_create_grouped_stash_accordion_empty() -> None:
    """Verify empty groups renders empty state alert."""
    accordion = create_grouped_stash_accordion([])
    empty_state = find_component_by_id(accordion, "stash-empty-state")
    assert empty_state is not None
    assert "No stash items found" in str(empty_state.to_plotly_json())


# ---------------------------------------------------------------------------
# 6. Layout Tests
# ---------------------------------------------------------------------------


def test_create_stash_layout_structure() -> None:
    """Verify Personal Stash layout has sync bar, search input, sort dropdown, list container, pagination, and stores."""
    layout = create_stash_layout(items=make_sample_stash_items())

    # Sync controls
    sync_btn = find_component_by_id(layout, "stash-sync-btn")
    assert sync_btn is not None

    pending_badge = find_component_by_id(layout, "stash-pending-badge")
    assert pending_badge is not None

    last_synced = find_component_by_id(layout, "stash-last-synced")
    assert last_synced is not None

    # Filter & Sort controls
    search_input = find_component_by_id(layout, "stash-search-input")
    assert search_input is not None

    search_btn = find_component_by_id(layout, "stash-search-btn")
    assert search_btn is not None
    assert "Search" in str(search_btn.to_plotly_json())
    assert "bi-search" in str(search_btn.to_plotly_json())

    sort_dropdown = find_component_by_id(layout, "stash-sort-dropdown")
    assert sort_dropdown is not None

    # List container wrapped in spinner
    list_container = find_component_by_id(layout, "stash-list-container")
    assert list_container is not None

    spinner = next((c for c in layout.children if isinstance(c, dbc.Spinner)), None)
    assert spinner is not None
    assert getattr(spinner, "color", None) == "primary"
    assert getattr(spinner, "type", None) == "border"
    assert getattr(spinner, "size", None) == "md"

    # Pagination controls
    pagination = find_component_by_id(layout, "stash-pagination")
    assert pagination is not None

    page_info = find_component_by_id(layout, "stash-pagination-info")
    assert page_info is not None

    # Raw store
    raw_store = find_component_by_id(layout, "stash-raw-store")
    assert raw_store is not None


# ---------------------------------------------------------------------------
# 7. Reactive Callbacks Tests
# ---------------------------------------------------------------------------


def test_stash_callbacks_registration() -> None:
    """Verify register_stash_callbacks attaches callbacks to Dash app without error."""
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    app.layout = create_stash_layout(items=make_sample_stash_items())

    # Register callbacks
    register_stash_callbacks(app)
    assert len(app.callback_map) >= 1

    # Verify search button and submit inputs are registered
    stash_callback_key = next((k for k in app.callback_map if "stash-list-container" in k), None)
    assert stash_callback_key is not None
    stash_callback = app.callback_map[stash_callback_key]
    input_ids = [inp["id"] for inp in stash_callback["inputs"]]
    assert "stash-search-btn" in input_ids
    assert "stash-search-input" in input_ids


def test_update_stash_view_callback_logic() -> None:
    """Verify update_stash_view_logic responds correctly to filter, sort, and pagination inputs."""
    raw_items = [item.model_dump() for item in make_sample_stash_items()]

    # 1. Filter by "Malabrigo"
    accordion, total_pages, page, info = update_stash_view_logic(
        search_query="Malabrigo",
        sort_by="brand_asc",
        active_page=1,
        raw_data=raw_items,
    )
    assert total_pages == 1
    assert page == 1
    assert "1 parent yarns" in info
    assert "Malabrigo — Rios" in str(accordion.to_plotly_json())

    # 2. No query, sort by qty_desc
    accordion, total_pages, page, info = update_stash_view_logic(
        search_query=None,
        sort_by="qty_desc",
        active_page=1,
        raw_data=raw_items,
    )
    assert total_pages == 1
    assert "3 parent yarns" in info

    # 3. Empty raw data
    accordion, total_pages, page, info = update_stash_view_logic(
        search_query=None,
        sort_by="brand_asc",
        active_page=1,
        raw_data=[],
    )
    assert total_pages == 1
    assert "No stash items found" in str(accordion.to_plotly_json())

    # 4. Search button click resets page to 1
    _accordion, _total_pages, page, _info = update_stash_view_logic(
        search_query="Malabrigo",
        sort_by="brand_asc",
        active_page=3,
        raw_data=raw_items,
        triggered_id="stash-search-btn",
    )
    assert page == 1

    # 5. Search input submit resets page to 1
    _accordion, _total_pages, page, _info = update_stash_view_logic(
        search_query="Malabrigo",
        sort_by="brand_asc",
        active_page=3,
        raw_data=raw_items,
        triggered_id="stash-search-input",
    )
    assert page == 1


def test_handle_stash_sync_callback_logic() -> None:
    """Verify handle_stash_sync_logic updates status and prevents update on 0 clicks."""
    # PreventUpdate on 0 clicks
    with pytest.raises(dash.exceptions.PreventUpdate):
        handle_stash_sync_logic(0, [])

    with pytest.raises(dash.exceptions.PreventUpdate):
        handle_stash_sync_logic(None, [])

    # Clicked with success
    status, color, last_synced, fresh_items = handle_stash_sync_logic(1, [])
    assert status == "Synced"
    assert color == "success"
    assert "Last synced: Today" in last_synced
    assert fresh_items == []

    # Clicked with client error
    mock_client = MagicMock()
    mock_client.get_my_stash.side_effect = RuntimeError("API unreachable")
    err_status, err_color, err_synced, err_items = handle_stash_sync_logic(1, [{"id": 1}], client=mock_client)
    assert err_status == "Sync Failed"
    assert err_color == "danger"
    assert "Sync failed" in err_synced
    assert err_items == [{"id": 1}]


