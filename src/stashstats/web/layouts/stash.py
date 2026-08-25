"""Personal Stash tab page layout with search filter, sort selector, and pagination controls."""

from typing import Any

import dash_bootstrap_components as dbc
from dash import dcc, html

from stashstats.models.stash import StashItem
from stashstats.web.components.modal import create_stash_modal
from stashstats.web.components.stash import (
    create_grouped_stash_accordion,
    filter_stash_groups,
    group_stash_items,
    paginate_stash_groups,
    sort_stash_groups,
)


def create_stash_layout(
    items: list[StashItem] | list[dict[str, Any]] | None = None,
    sync_status: str = "Synced",
    pending_count: int = 0,
    last_synced: str | None = None,
    query: str = "",
    sort_by: str = "brand_asc",
    page: int = 1,
    page_size: int = 25,
    include_stores: bool = True,
) -> dbc.Container:
    """Create the Personal Stash interface layout.

    Args:
        items: Optional list of StashItem objects or dictionary payloads.
        sync_status: Status string for the sync status badge.
        pending_count: Count of pending changes.
        last_synced: Timestamp of last successful sync.
        query: Initial search/filter string.
        sort_by: Initial sorting option key.
        page: Current active page number (1-indexed).
        page_size: Stash items per page count.
        include_stores: Whether to include dcc.Store components in the container.

    Returns:
        Configured dbc.Container component.
    """
    raw_items = items or []
    groups = group_stash_items(raw_items)
    filtered = filter_stash_groups(groups, query)
    sorted_groups = sort_stash_groups(filtered, sort_by)
    paginated_groups, total_pages = paginate_stash_groups(
        sorted_groups, page=page, page_size=page_size
    )

    # 1. Top Controls: Sync Bar
    sync_btn = dbc.Button(
        [html.I(className="bi bi-arrow-repeat me-1"), "Sync Now"],
        id="stash-sync-btn",
        color="success",
        size="sm",
        className="fw-semibold me-2 d-flex align-items-center",
    )

    if pending_count > 0:
        pending_badge_text = f"{pending_count} pending"
        pending_badge_color = "warning"
    else:
        pending_badge_text = sync_status
        pending_badge_color = "success"

    pending_badge = dbc.Badge(
        pending_badge_text,
        color=pending_badge_color,
        pill=True,
        className="me-2 px-2 py-1 align-self-center",
        id="stash-pending-badge",
    )

    last_synced_text = f"Last synced: {last_synced}" if last_synced else "Last synced: Never"
    last_synced_elem = html.Small(
        last_synced_text,
        className="text-muted align-self-center",
        id="stash-last-synced",
    )

    sync_row = dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        sync_btn,
                        pending_badge,
                        last_synced_elem,
                    ],
                    className="d-flex align-items-center mb-3",
                ),
                xs=12,
            )
        ]
    )

    # 2. Search & Sort Controls Row
    search_input = dbc.InputGroup(
        [
            dbc.InputGroupText(
                html.I(className="bi bi-search text-muted"),
                className="bg-dark border-secondary",
            ),
            dbc.Input(
                id="stash-search-input",
                type="search",
                placeholder="Filter stash by yarn name, brand, or colorway...",
                value=query,
                debounce=True,
                className="bg-dark text-light border-secondary",
            ),
            dbc.Button(
                [html.I(className="bi bi-search me-1"), "Search"],
                id="stash-search-btn",
                color="primary",
                className="fw-semibold",
            ),
        ],
        className="mb-2 mb-md-0",
    )

    sort_options = [
        {"label": "Brand (A-Z)", "value": "brand_asc"},
        {"label": "Name (A-Z)", "value": "name_asc"},
        {"label": "Quantity (High-Low)", "value": "qty_desc"},
        {"label": "Date Added (Newest)", "value": "date_desc"},
    ]

    sort_dropdown = dbc.InputGroup(
        [
            dbc.InputGroupText(
                html.I(className="bi bi-sort-down text-muted"),
                className="bg-dark border-secondary",
            ),
            dbc.Select(
                id="stash-sort-dropdown",
                options=sort_options,
                value=sort_by,
                className="bg-dark text-light border-secondary",
            ),
        ]
    )

    filter_row = dbc.Row(
        [
            dbc.Col(search_input, xs=12, md=8, lg=9),
            dbc.Col(sort_dropdown, xs=12, md=4, lg=3),
        ],
        className="mb-3 g-2",
    )

    # 3. Stash Grouped Accordion List Container
    accordion_component = create_grouped_stash_accordion(paginated_groups)
    list_container = html.Div(
        accordion_component,
        id="stash-list-container",
        className="stash-items-wrapper",
    )
    list_spinner = dbc.Spinner(
        list_container,
        color="primary",
        type="border",
        size="md",
    )

    # 4. Pagination Controls
    pagination = dbc.Pagination(
        id="stash-pagination",
        active_page=page,
        max_value=total_pages,
        fully_expanded=False,
        previous_next=True,
        first_last=True,
        className="justify-content-center mt-3",
    )

    info_text = f"Showing page {page} of {total_pages} ({len(filtered)} parent yarns)"
    pagination_info = html.Div(
        info_text,
        id="stash-pagination-info",
        className="text-muted text-center small mt-1",
    )

    pagination_container = html.Div(
        [
            pagination,
            pagination_info,
        ],
        id="stash-pagination-container",
        className="mt-3 mb-4",
    )

    # 5. Data Stores
    stores = []
    if include_stores:
        serialized_items = [
            item.model_dump() if hasattr(item, "model_dump") else item
            for item in raw_items
        ]
        stores = [
            dcc.Store(id="stash-raw-store", data=serialized_items),
            dcc.Store(id="stash-dirty-store", data=[]),
        ]

    # 6. Modal Dialog
    modal = create_stash_modal()

    return dbc.Container(
        [
            *stores,
            sync_row,
            filter_row,
            list_spinner,
            pagination_container,
            modal,
        ],
        fluid=True,
        id="personal-stash-container",
        className="p-0",
    )
