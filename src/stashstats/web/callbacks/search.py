"""Reactive callbacks for Yarn Search form inputs, API search execution, and pagination."""

import logging
from typing import Any

import dash
import dash_bootstrap_components as dbc
from dash import MATCH, Input, Output, State, ctx, html

from datetime import UTC, datetime

from stashstats.client import RavelryClient
from stashstats.web.components.search import create_yarn_search_accordion


logger = logging.getLogger(__name__)


def build_search_query(query: str | None, brand: str | None) -> str:

    """Build unified search query string combining brand and keyword filters.

    Args:
        query: User keyword search string.
        brand: Brand / yarn company filter string.

    Returns:
        Cleaned combined query string for the Ravelry API.
    """
    clean_brand = brand.strip() if brand else ""
    clean_query = query.strip() if query else ""

    parts = [p for p in [clean_brand, clean_query] if p]
    return " ".join(parts)


SORT_MAPPING = {
    "best_match": "best",
    "highest_rating": "rating",
    "most_projects": "projects",
    "best": "best",
    "rating": "rating",
    "projects": "projects",
}


def update_yarn_search_logic(
    client: RavelryClient | None,
    query: str | None,
    brand: str | None,
    sort: str | None = "best_match",
    active_page: int | None = 1,
    page_size: int = 25,
    allow_empty_search: bool = False,
) -> tuple[Any, int, int, str, list[dict[str, Any]], dict[str, Any]]:
    """Execute yarn search against Ravelry API and format UI results.

    Args:
        client: Authenticated RavelryClient instance (or None if offline).
        query: Search keyword string.
        brand: Brand name filter string.
        sort: Sort category selection.
        active_page: Target page number (1-indexed).
        page_size: Results per page count.
        allow_empty_search: Whether to execute search even when query string is empty.

    Returns:
        Tuple containing:
        - Accordion component or alert container
        - Total page count (int)
        - Clamped active page (int)
        - Pagination info summary text (str)
        - Serialized yarn search results list
        - Paginator metadata state dictionary
    """
    clean_query = query.strip() if query else ""
    clean_brand = brand.strip() if brand else ""
    search_str = build_search_query(clean_query, clean_brand)
    api_sort = SORT_MAPPING.get(sort or "best_match", "best")

    # 1. Missing client -> prominent warning Alert indicating API credentials / client missing in .env
    if client is None:
        warning_elem = html.Div(
            dbc.Alert(
                [
                    html.I(className="bi bi-exclamation-triangle me-2"),
                    html.Strong("Ravelry API Client Unavailable: "),
                    "API credentials / client missing in .env. Please configure your credentials to enable yarn search.",
                ],
                color="warning",
                className="text-center my-4",
            ),
            id="yarn-search-warning-state",
        )
        return (
            warning_elem,
            1,
            1,
            "Ravelry API credentials / client missing in .env",
            [],
            {
                "page": 1,
                "total_pages": 1,
                "total_results": 0,
                "query": clean_query,
                "brand": clean_brand,
                "sort": sort,
            },
        )

    # 2. Empty search input -> return empty search state with informative info text if not explicitly searching
    if not search_str and not allow_empty_search:
        accordion = create_yarn_search_accordion([])
        return (
            accordion,
            1,
            1,
            "Enter a keyword or brand to search yarns.",
            [],
            {
                "page": 1,
                "total_pages": 1,
                "total_results": 0,
                "query": clean_query,
                "brand": clean_brand,
                "sort": sort,
            },
        )

    page_num = max(1, active_page) if active_page is not None else 1

    try:
        response = client.search_yarns(
            query=search_str,
            page=page_num,
            page_size=page_size,
            sort=api_sort,
        )

        yarns = response.yarns
        paginator = response.paginator
        total_pages = max(1, paginator.page_count if paginator else 1)
        clamped_page = max(1, min(page_num, total_pages))
        total_results = paginator.results if paginator else len(yarns)

        accordion = create_yarn_search_accordion(yarns)
        info_text = f"Showing page {clamped_page} of {total_pages} ({total_results} yarns found)"
        serialized_yarns = [
            y.model_dump() if hasattr(y, "model_dump") else y for y in yarns
        ]
        paginator_data = {
            "page": clamped_page,
            "total_pages": total_pages,
            "total_results": total_results,
            "query": clean_query,
            "brand": clean_brand,
            "sort": sort,
        }

        return (
            accordion,
            total_pages,
            clamped_page,
            info_text,
            serialized_yarns,
            paginator_data,
        )

    except Exception as exc:
        logger.exception("Error querying Ravelry yarn search")
        error_elem = html.Div(
            dbc.Alert(
                [
                    html.I(className="bi bi-exclamation-triangle me-2"),
                    f"Error searching yarns: {exc}",
                ],
                color="danger",
                className="text-center my-4",
            ),
            id="yarn-search-error-state",
        )
        return (
            error_elem,
            1,
            1,
            f"Search error: {exc}",
            [],
            {
                "page": 1,
                "total_pages": 1,
                "total_results": 0,
                "query": clean_query,
                "brand": clean_brand,
                "sort": sort,
            },
        )


def handle_yarn_search_callback(
    client: RavelryClient | None,
    triggered_id: Any,
    n_clicks: int | None,
    query_submit: int | None,
    brand_submit: int | None,
    sort_val: str | None,
    active_page: int | None,
    query_val: str | None,
    brand_val: str | None,
    paginator_store: dict[str, Any] | None,
    page_size: int = 25,
) -> tuple[Any, int, int, str, list[dict[str, Any]], dict[str, Any]]:
    """Parse trigger sources, determine target query/page, and run search."""
    if not triggered_id and not any([n_clicks, query_submit, brand_submit, sort_val, active_page]):
        raise dash.exceptions.PreventUpdate

    if triggered_id == "yarn-search-pagination":
        # Pagination click -> preserve previous search query/brand/sort from store
        query = (paginator_store or {}).get("query", query_val)
        brand = (paginator_store or {}).get("brand", brand_val)
        sort = (paginator_store or {}).get("sort", sort_val)
        page = active_page or 1
    else:
        # Search button, Enter submit, or Sort change -> search starting at page 1
        query = query_val
        brand = brand_val
        sort = sort_val
        page = 1

    allow_empty = bool(triggered_id in ("yarn-search-btn", "yarn-search-query-input", "yarn-search-brand-input", "yarn-search-sort-input", "yarn-search-pagination"))
    return update_yarn_search_logic(
        client=client,
        query=query,
        brand=brand,
        sort=sort,
        active_page=page,
        page_size=page_size,
        allow_empty_search=allow_empty,
    )


def handle_add_to_stash_logic(
    client: RavelryClient | None,
    yarn_id: int,
    skeins: float | None,
    colorway: str | None,
    dyelot: str | None,
    location: str | None,
    notes: str | None,
    date_added: str | None,
    search_results: list[dict[str, Any]] | None,
    raw_stash_items: list[dict[str, Any]] | None,
) -> tuple[str, list[dict[str, Any]]]:
    """Execute creation of a new stash item and prepend to raw stash store.

    Args:
        client: Optional authenticated RavelryClient instance.
        yarn_id: Catalog yarn database ID.
        skeins: Decimal number of skeins.
        colorway: Colorway name.
        dyelot: Dye lot identifier.
        location: Storage location string.
        notes: User stash notes.
        date_added: YYYY-MM-DD date string.
        search_results: Cached yarn search results list.
        raw_stash_items: Current stash-raw-store item records.

    Returns:
        Tuple of (status_message_str, updated_stash_items_list).
    """
    skeins_val = float(skeins) if skeins and float(skeins) > 0 else 1.0

    # Look up yarn metadata from search results
    yarn_data: dict[str, Any] = {}
    for y in (search_results or []):
        if str(y.get("id")) == str(yarn_id):
            yarn_data = dict(y)
            break

    yarn_name = yarn_data.get("name") or f"Yarn #{yarn_id}"
    brand_name = yarn_data.get("yarn_company_name") or ""
    grams_per_skein = float(yarn_data.get("grams") or 100.0)
    yards_per_skein = float(yarn_data.get("yardage") or 200.0)
    total_yards = round(yards_per_skein * skeins_val, 2)
    total_grams = round(grams_per_skein * skeins_val, 2)
    total_meters = round(total_yards * 0.9144, 2)

    new_stash_dict: dict[str, Any] | None = None

    if client is not None:
        try:
            created_item = client.create_stash_item(
                yarn_id=yarn_id,
                colorway_name=colorway,
                dye_lot=dyelot,
                skeins=skeins_val,
                total_grams=total_grams,
                total_yards=total_yards,
                location=location,
                stash_status_id=1,
            )
            new_stash_dict = created_item.model_dump() if hasattr(created_item, "model_dump") else dict(created_item)
        except Exception as exc:
            logger.warning(f"Failed to create stash item in Ravelry API: {exc}")

    if not new_stash_dict:
        full_name = f"{brand_name} {yarn_name}".strip() if brand_name else yarn_name
        new_stash_dict = {
            "id": int(datetime.now(tz=UTC).timestamp() * 1000),
            "name": full_name,
            "permalink": yarn_data.get("permalink") or f"yarn-{yarn_id}",
            "colorway_name": colorway,
            "dye_lot": dyelot,
            "location": location,
            "notes": notes,
            "skeins": skeins_val,
            "total_yards": total_yards,
            "total_grams": total_grams,
            "total_meters": total_meters,
            "created_at": date_added or datetime.now(tz=UTC).isoformat(),
            "stash_status": {"id": 1, "name": "In stash"},
            "yarn": {
                "id": yarn_id,
                "name": yarn_name,
                "yarn_company_name": brand_name,
                "yarn_weight": yarn_data.get("yarn_weight"),
            },
            "packs": [
                {
                    "id": int(datetime.now(tz=UTC).timestamp() * 1000) + 1,
                    "colorway": colorway,
                    "dye_lot": dyelot,
                    "skeins": skeins_val,
                    "total_yards": total_yards,
                    "total_grams": total_grams,
                }
            ],
        }

    updated_stash = [new_stash_dict] + [dict(it) for it in (raw_stash_items or [])]
    status_msg = f"Successfully added {skeins_val:g} skein(s) of {yarn_name} to stash!"

    return status_msg, updated_stash


def register_search_callbacks(app: dash.Dash) -> None:
    """Register all interactive reactive callbacks for the Yarn Search view.

    Args:
        app: The Dash application instance.
    """
    if getattr(app, "_search_callbacks_registered", False):
        return
    app._search_callbacks_registered = True  # type: ignore[attr-defined]

    @app.callback(
        Output("yarn-search-list-container", "children"),
        Output("yarn-search-pagination", "max_value"),
        Output("yarn-search-pagination", "active_page"),
        Output("yarn-search-pagination-info", "children"),
        Output("yarn-search-results-store", "data"),
        Output("yarn-search-paginator-store", "data"),
        Input("yarn-search-btn", "n_clicks"),
        Input("yarn-search-query-input", "n_submit"),
        Input("yarn-search-brand-input", "n_submit"),
        Input("yarn-search-sort-input", "value"),
        Input("yarn-search-pagination", "active_page"),
        State("yarn-search-query-input", "value"),
        State("yarn-search-brand-input", "value"),
        State("yarn-search-paginator-store", "data"),
        prevent_initial_call=True,
    )
    def handle_search(
        n_clicks: int | None,
        query_submit: int | None,
        brand_submit: int | None,
        sort_val: str | None,
        active_page: int | None,
        query_val: str | None,
        brand_val: str | None,
        paginator_store: dict[str, Any] | None,
    ) -> tuple[Any, int, int, str, list[dict[str, Any]], dict[str, Any]]:
        client = getattr(app, "client", None)
        return handle_yarn_search_callback(
            client=client,
            triggered_id=ctx.triggered_id,
            n_clicks=n_clicks,
            query_submit=query_submit,
            brand_submit=brand_submit,
            sort_val=sort_val,
            active_page=active_page,
            query_val=query_val,
            brand_val=brand_val,
            paginator_store=paginator_store,
        )

    @app.callback(
        Output({"type": "stash-status-msg", "index": MATCH}, "children"),
        Output("stash-raw-store", "data", allow_duplicate=True),
        Input({"type": "stash-submit-btn", "index": MATCH}, "n_clicks"),
        State({"type": "stash-skeins", "index": MATCH}, "value"),
        State({"type": "stash-colorway", "index": MATCH}, "value"),
        State({"type": "stash-dyelot", "index": MATCH}, "value"),
        State({"type": "stash-location", "index": MATCH}, "value"),
        State({"type": "stash-notes", "index": MATCH}, "value"),
        State({"type": "stash-date-added", "index": MATCH}, "date"),
        State({"type": "stash-submit-btn", "index": MATCH}, "id"),
        State("yarn-search-results-store", "data"),
        State("stash-raw-store", "data"),
        prevent_initial_call=True,
    )
    def handle_add_to_stash(
        n_clicks: int | None,
        skeins: float | None,
        colorway: str | None,
        dyelot: str | None,
        location: str | None,
        notes: str | None,
        date_added: str | None,
        btn_id: dict[str, Any],
        search_results: list[dict[str, Any]] | None,
        raw_stash_items: list[dict[str, Any]] | None,
    ) -> tuple[str, list[dict[str, Any]]]:
        if not n_clicks:
            raise dash.exceptions.PreventUpdate
        client = getattr(app, "client", None)
        yarn_id = int(btn_id.get("index")) if isinstance(btn_id, dict) else int(btn_id)
        return handle_add_to_stash_logic(
            client=client,
            yarn_id=yarn_id,
            skeins=skeins,
            colorway=colorway,
            dyelot=dyelot,
            location=location,
            notes=notes,
            date_added=date_added,
            search_results=search_results,
            raw_stash_items=raw_stash_items,
        )
