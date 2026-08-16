"""End-to-end integration tests for the full StashStats web dashboard.

Tests complete application assembly, header, tabs, stash inventory view, modal dialogs,
reactive callbacks, data pipelines, and HTTP endpoint serving.
"""

from typing import Any

from dash.development.base_component import Component

from stashstats.client import RavelryClient
from stashstats.config import Settings
from stashstats.models.stash import Pack, StashItem, StashStatus, StashYarn
from stashstats.models.yarn import YarnWeight
from stashstats.web.app import create_app
from stashstats.web.callbacks.modal import (
    handle_save_modal,
    handle_usage_preview_update,
)
from stashstats.web.callbacks.stash import (
    handle_stash_sync_logic,
    update_stash_view_logic,
)
from stashstats.web.components.modal import (
    rollback_usage_from_stash,
)
from stashstats.web.components.stash import (
    group_stash_items,
    paginate_stash_groups,
    sort_stash_groups,
)


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


def find_all_components(tree: Any, predicate: Any) -> list[Component]:
    """Recursively find all components in tree matching predicate."""
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


def make_integration_stash_items() -> list[StashItem]:
    """Create realistic sample stash dataset for integration testing."""
    return [
        StashItem(
            id=1,
            name="Malabrigo Rios - Diana",
            permalink="stash-malabrigo-rios-diana",
            colorway_name="Diana",
            dye_lot="Lot-401",
            location="Bin 1 - Worsted",
            skeins=4.0,
            total_yards=840.0,
            total_grams=400.0,
            notes="Sweater quantity in vibrant purple/teal",
            stash_status=StashStatus(id=1, name="In stash"),
            yarn=StashYarn(
                id=10,
                name="Rios",
                yarn_company_name="Malabrigo",
                yarn_weight=YarnWeight(id=4, name="Worsted", ply="4", wpi="9"),
            ),
            packs=[
                Pack(
                    id=101,
                    skeins=4.0,
                    total_yards=840.0,
                    total_grams=400.0,
                    colorway_name="Diana",
                    dye_lot="Lot-401",
                )
            ],
            created_at="2026-01-10T12:00:00Z",
        ),
        StashItem(
            id=2,
            name="Malabrigo Rios - Paris Night",
            permalink="stash-malabrigo-rios-paris-night",
            colorway_name="Paris Night",
            dye_lot="Lot-402",
            location="Bin 1 - Worsted",
            skeins=2.0,
            total_yards=420.0,
            total_grams=200.0,
            notes="Deep midnight navy blue",
            stash_status=StashStatus(id=1, name="In stash"),
            yarn=StashYarn(
                id=10,
                name="Rios",
                yarn_company_name="Malabrigo",
                yarn_weight=YarnWeight(id=4, name="Worsted", ply="4", wpi="9"),
            ),
            packs=[
                Pack(
                    id=102,
                    skeins=2.0,
                    total_yards=420.0,
                    total_grams=200.0,
                    colorway_name="Paris Night",
                    dye_lot="Lot-402",
                )
            ],
            created_at="2026-02-15T10:30:00Z",
        ),
        StashItem(
            id=3,
            name="Madelinetosh Tosh Merino Light - Tart",
            permalink="stash-madelinetosh-tml-tart",
            colorway_name="Tart",
            dye_lot="Lot-99",
            location="Bin 2 - Fingering",
            skeins=3.0,
            total_yards=1260.0,
            total_grams=300.0,
            notes="Bright cherry red",
            stash_status=StashStatus(id=1, name="In stash"),
            yarn=StashYarn(
                id=20,
                name="Tosh Merino Light",
                yarn_company_name="Madelinetosh",
                yarn_weight=YarnWeight(id=1, name="Fingering", ply="1", wpi="14"),
            ),
            packs=[
                Pack(
                    id=103,
                    skeins=3.0,
                    total_yards=1260.0,
                    total_grams=300.0,
                    colorway_name="Tart",
                    dye_lot="Lot-99",
                )
            ],
            created_at="2026-03-01T08:00:00Z",
        ),
        StashItem(
            id=4,
            name="Cascade 220 - Sapphire",
            permalink="stash-cascade-220-sapphire",
            colorway_name="Sapphire",
            dye_lot="Lot-12",
            location="Bin 1 - Worsted",
            skeins=1.0,
            total_yards=220.0,
            total_grams=100.0,
            notes="Single skein remnant",
            stash_status=StashStatus(id=2, name="Used up"),
            yarn=StashYarn(
                id=30,
                name="220",
                yarn_company_name="Cascade Yarns",
                yarn_weight=YarnWeight(id=4, name="Worsted", ply="4", wpi="9"),
            ),
            packs=[
                Pack(
                    id=104,
                    skeins=1.0,
                    total_yards=220.0,
                    total_grams=100.0,
                    colorway_name="Sapphire",
                    dye_lot="Lot-12",
                )
            ],
            created_at="2025-11-20T14:00:00Z",
        ),
    ]


# ===========================================================================
# 1. Full Application Layout & Component Assembly
# ===========================================================================


def test_full_application_assembly() -> None:
    """Verify create_app builds complete Darkly-themed shell with all subcomponents."""
    items = make_integration_stash_items()
    client = RavelryClient(
        settings=Settings(access_key="dummy_key", personal_key="dummy_secret")
    )
    client._cached_username = "fiberfanatic"

    app = create_app(client=client, items=items)

    layout = app.layout
    assert getattr(layout, "id", None) == "app-root"

    # Header components
    assert find_component_by_id(layout, "global-header") is not None
    assert find_component_by_id(layout, "header-brand") is not None
    user_badge = find_component_by_id(layout, "header-user-badge")
    assert user_badge is not None
    assert "@fiberfanatic" in str(user_badge.to_plotly_json())
    assert find_component_by_id(layout, "header-sync-indicator") is not None
    assert find_component_by_id(layout, "header-sync-badge") is not None

    # Navigation tabs
    assert find_component_by_id(layout, "main-tabs") is not None
    assert find_component_by_id(layout, "tab-stash-nav") is not None
    assert find_component_by_id(layout, "tab-analytics-nav") is not None
    assert find_component_by_id(layout, "tab-projects-nav") is not None
    assert find_component_by_id(layout, "tab-search-nav") is not None

    # Tab content container
    assert find_component_by_id(layout, "tab-content") is not None
    assert find_component_by_id(layout, "stash-tab-content") is not None
    assert find_component_by_id(layout, "analytics-tab-content") is not None
    assert find_component_by_id(layout, "projects-tab-content") is not None
    assert find_component_by_id(layout, "search-tab-content") is not None
    assert find_component_by_id(layout, "personal-stash-container") is not None

    # Stash controls
    assert find_component_by_id(layout, "stash-sync-btn") is not None
    assert find_component_by_id(layout, "stash-pending-badge") is not None
    assert find_component_by_id(layout, "stash-last-synced") is not None
    assert find_component_by_id(layout, "stash-search-input") is not None
    assert find_component_by_id(layout, "stash-sort-dropdown") is not None
    assert find_component_by_id(layout, "stash-list-container") is not None
    assert find_component_by_id(layout, "stash-pagination") is not None
    assert find_component_by_id(layout, "stash-pagination-info") is not None

    # Data stores
    assert find_component_by_id(layout, "stash-raw-store") is not None
    assert find_component_by_id(layout, "stash-dirty-store") is not None

    # Modal dialog in layout
    assert find_component_by_id(layout, "stash-modal") is not None
    modal_tabs = find_component_by_id(layout, "modal-tabs")
    assert modal_tabs is not None
    tabs_json = str(modal_tabs.to_plotly_json())
    assert "tab-edit-details" in tabs_json
    assert "tab-log-usage" in tabs_json
    assert find_component_by_id(layout, "modal-input-colorway") is not None
    assert find_component_by_id(layout, "modal-input-skeins") is not None
    assert find_component_by_id(layout, "modal-input-skeins-used") is not None
    assert find_component_by_id(layout, "modal-btn-save") is not None
    assert find_component_by_id(layout, "modal-btn-cancel") is not None


def test_application_callbacks_registered() -> None:
    """Verify all callbacks for stash, modal, and yarn search are registered on Dash app."""
    app = create_app()
    assert len(app.callback_map) >= 5

    outputs = list(app.callback_map.keys())
    # Verify stash callbacks
    assert any("stash-list-container" in o for o in outputs)
    assert any("stash-pending-badge" in o for o in outputs)
    # Verify modal callbacks
    assert any("modal-usage-preview" in o for o in outputs)
    assert any("stash-modal" in o for o in outputs)
    # Verify search callbacks
    assert any("yarn-search-list-container" in o for o in outputs)



# ===========================================================================
# 2. End-to-End Inventory Grouping, Filtering, & Sorting Pipelines
# ===========================================================================


def test_stash_inventory_grouping_e2e() -> None:
    """Verify stash items are correctly aggregated by parent yarn."""
    items = make_integration_stash_items()
    groups = group_stash_items(items)

    # 4 items grouped across 3 parent yarns: Malabrigo Rios (2 items), Tosh Merino Light (1), Cascade 220 (1)
    assert len(groups) == 3

    rios_group = next(g for g in groups if "Rios" in g.yarn_name)
    assert rios_group.brand_name == "Malabrigo"
    assert rios_group.total_items == 2
    assert rios_group.total_skeins == 6.0  # 4.0 + 2.0
    assert rios_group.total_yards == 1260.0  # 840.0 + 420.0
    assert rios_group.total_grams == 600.0  # 400.0 + 200.0
    assert len(rios_group.items) == 2


def test_stash_filter_search_pipeline() -> None:
    """Verify live search filtering accurately narrows down parent yarn groups."""
    items = [item.model_dump() for item in make_integration_stash_items()]

    # 1. Search for "Rios" -> Only Malabrigo Rios returned
    acc, _total_pages, _page, info = update_stash_view_logic("Rios", "brand_asc", 1, items)
    assert "Showing page 1 of 1 (1 parent yarns)" in info
    acc_json = str(acc.to_plotly_json())
    assert "Malabrigo — Rios" in acc_json
    assert "Cascade" not in acc_json
    assert "Madelinetosh" not in acc_json

    # 2. Search for "Tart" (colorway query) -> Only Tosh Merino Light returned
    acc, _total_pages, _page, info = update_stash_view_logic("Tart", "brand_asc", 1, items)
    assert "Showing page 1 of 1 (1 parent yarns)" in info
    acc_json = str(acc.to_plotly_json())
    assert "Madelinetosh — Tosh Merino Light" in acc_json
    assert "Tart" in acc_json

    # 3. Search for nonexistent term -> 0 parent yarns found
    acc, _total_pages, _page, info = update_stash_view_logic(
        "NonexistentYarn", "brand_asc", 1, items
    )
    assert "0 parent yarns" in info
    assert "No stash items found" in str(acc.to_plotly_json())


def test_stash_sorting_pipeline() -> None:
    """Verify sorting parent groups by various criteria."""
    items = make_integration_stash_items()
    groups = group_stash_items(items)

    # Brand Ascending: Cascade Yarns, Madelinetosh, Malabrigo
    sorted_brand = sort_stash_groups(groups, "brand_asc")
    assert sorted_brand[0].brand_name == "Cascade Yarns"
    assert sorted_brand[1].brand_name == "Madelinetosh"
    assert sorted_brand[2].brand_name == "Malabrigo"

    # Quantity Descending: Malabrigo (6.0 sk), Madelinetosh (3.0 sk), Cascade (1.0 sk)
    sorted_qty = sort_stash_groups(groups, "qty_desc")
    assert sorted_qty[0].brand_name == "Malabrigo"
    assert sorted_qty[0].total_skeins == 6.0
    assert sorted_qty[1].total_skeins == 3.0
    assert sorted_qty[2].total_skeins == 1.0


def test_stash_pagination_pipeline() -> None:
    """Verify pagination with multiple pages."""
    # Create 25 mock groups
    items = []
    for i in range(25):
        items.append(
            StashItem(
                id=i + 1,
                name=f"Brand {i // 5} Yarn {i}",
                permalink=f"stash-item-{i + 1}",
                colorway_name=f"Colorway {i}",
                skeins=2.0,
                stash_status=StashStatus(id=1, name="In stash"),
                yarn=StashYarn(id=i, name=f"Yarn {i}", yarn_company_name=f"Brand {i // 5}"),
            )
        )
    groups = group_stash_items(items)
    assert len(groups) == 25

    # Page 1 of 10 items
    p1, total_pages = paginate_stash_groups(groups, page=1, page_size=10)
    assert len(p1) == 10
    assert total_pages == 3

    # Page 3 of 5 items
    p3, total_pages = paginate_stash_groups(groups, page=3, page_size=10)
    assert len(p3) == 5


def test_stash_sync_interaction_pipeline() -> None:
    """Verify triggering sync updates badge and timestamp."""
    items = [item.model_dump() for item in make_integration_stash_items()]
    badge_text, badge_color, last_synced = handle_stash_sync_logic(n_clicks=1, raw_data=items)
    assert badge_text == "Synced"
    assert badge_color == "success"
    assert "Last synced:" in last_synced


# ===========================================================================
# 3. End-to-End Modal Usage Logging & History Rollback
# ===========================================================================


def test_modal_usage_deduction_and_save_workflow() -> None:
    """Verify logging usage correctly recalculates remaining stash and updates history."""
    stash_item = {
        "id": 1,
        "name": "Malabrigo Rios - Diana",
        "colorway_name": "Diana",
        "skeins": 4.0,
        "total_yards": 840.0,
        "total_grams": 400.0,
        "yarn_name": "Rios",
        "brand_name": "Malabrigo",
    }
    history: list[dict[str, Any]] = []

    # 1. User enters 1.5 skeins used -> Preview calculates remaining
    preview = handle_usage_preview_update(used_skeins=1.5, stash_data=stash_item)
    preview_json = str(preview.to_plotly_json())
    assert "Currently have: 4.0 skeins" in preview_json
    assert "Used: 1.5 skeins" in preview_json
    assert "Remaining: 2.5 skeins" in preview_json

    # 2. User clicks Save on "tab-log-usage" -> Updates stash and prepends history entry
    is_open, updated_stash, updated_history = handle_save_modal(
        n_clicks=1,
        active_tab="tab-log-usage",
        colorway=None,
        dye_lot=None,
        location=None,
        skeins=None,
        status=None,
        notes="Knitted a winter beanie",
        used_skeins=1.5,
        date_used="2026-04-10",
        stash_data=stash_item,
        history_data=history,
    )

    assert is_open is False  # Modal closes
    assert updated_stash["skeins"] == 2.5
    assert updated_stash["total_yards"] == 525.0  # 840 - (1.5 * 210)
    assert updated_stash["total_grams"] == 250.0  # 400 - (1.5 * 100)

    assert len(updated_history) == 1
    entry = updated_history[0]
    assert entry["skeins"] == -1.5
    assert entry["yards"] == -315.0
    assert entry["grams"] == -150.0
    assert entry["date"] == "2026-04-10"
    assert entry["notes"] == "Knitted a winter beanie"


def test_modal_history_rollback_workflow() -> None:
    """Verify deleting a usage history event restores deducted skeins and yardage."""
    # Stash state after 1.5 skeins were used
    current_stash = {
        "id": 1,
        "name": "Malabrigo Rios - Diana",
        "colorway_name": "Diana",
        "skeins": 2.5,
        "total_yards": 525.0,
        "total_grams": 250.0,
    }
    history = [
        {
            "id": "entry-uuid-1",
            "skeins": -1.5,
            "yards": -315.0,
            "grams": -150.0,
            "date": "2026-04-10",
            "notes": "Beanie",
        }
    ]

    restored_stash, remaining_history = rollback_usage_from_stash(
        stash_item=current_stash,
        usage_index=0,
        history=history,
    )

    assert restored_stash["skeins"] == 4.0
    assert restored_stash["total_yards"] == 840.0
    assert restored_stash["total_grams"] == 400.0
    assert len(remaining_history) == 0


def test_modal_edit_details_save_workflow() -> None:
    """Verify saving Tab 1 (Edit Details) updates metadata correctly."""
    stash_item = {
        "id": 1,
        "colorway_name": "Diana",
        "dye_lot": "Lot-401",
        "location": "Bin 1",
        "skeins": 4.0,
        "stash_status": {"name": "In stash"},
        "notes": "Old notes",
    }

    is_open, updated_stash, _history = handle_save_modal(
        n_clicks=1,
        active_tab="tab-edit-details",
        colorway="Diana (Special Edition)",
        dye_lot="Lot-401-B",
        location="Shelf 3A",
        skeins=5.0,
        status="Gifted",
        notes="Updated notes for project",
        used_skeins=None,
        date_used=None,
        stash_data=stash_item,
        history_data=[],
    )

    assert is_open is False
    assert updated_stash["colorway_name"] == "Diana (Special Edition)"
    assert updated_stash["dye_lot"] == "Lot-401-B"
    assert updated_stash["location"] == "Shelf 3A"
    assert updated_stash["skeins"] == 5.0
    assert updated_stash["stash_status"]["name"] == "Gifted"
    assert updated_stash["notes"] == "Updated notes for project"


# ===========================================================================
# 4. End-to-End HTTP Server Serving & ASGI/WSGI Integration
# ===========================================================================


def test_http_root_endpoint_serving() -> None:
    """Verify underlying Flask/WSGI server responds to HTTP GET with HTML shell."""
    app = create_app()
    server = app.server

    with server.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200
        html_content = response.get_data(as_text=True)
        assert "<title>StashStats</title>" in html_content
        assert "dash" in html_content.lower()


def test_http_dash_layout_endpoint() -> None:
    """Verify /_dash-layout endpoint returns complete JSON layout hierarchy."""
    app = create_app()
    server = app.server

    with server.test_client() as client:
        response = client.get("/_dash-layout")
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert "props" in data
        assert data["props"]["id"] == "app-root"


def test_http_dash_dependencies_endpoint() -> None:
    """Verify /_dash-dependencies endpoint returns registered callbacks."""
    app = create_app()
    server = app.server

    with server.test_client() as client:
        response = client.get("/_dash-dependencies")
        assert response.status_code == 200
        deps = response.get_json()
        assert isinstance(deps, list)
        assert len(deps) >= 4
