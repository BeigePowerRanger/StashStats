"""Reactive callbacks for Yarn Search form inputs, API search execution, and pagination."""

import logging
from typing import Any

import dash
import dash_bootstrap_components as dbc
from dash import ALL, MATCH, Input, Output, State, ctx, html

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

        # Enrich search results with official colorways from Ravelry API
        enriched_yarns = []
        for y in yarns:
            y_dict = y.model_dump() if hasattr(y, "model_dump") else dict(y)
            if not y_dict.get("colorways") and client and y_dict.get("id"):
                try:
                    detail = client.get_yarn_details(y_dict["id"])
                    if detail and detail.yarn and detail.yarn.colorways:
                        y_dict["colorways"] = [cw.name for cw in detail.yarn.colorways if cw.name]
                except Exception:
                    pass
            enriched_yarns.append(y_dict)

        accordion = create_yarn_search_accordion(enriched_yarns)
        info_text = f"Showing page {clamped_page} of {total_pages} ({total_results} yarns found)"
        serialized_yarns = enriched_yarns
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
    if not triggered_id and not any([n_clicks, query_submit, brand_submit, sort_val, active_page, query_val, brand_val]):
        raise dash.exceptions.PreventUpdate

    is_user_trigger = bool(
        triggered_id in (
            "yarn-search-btn",
            "yarn-search-query-input",
            "yarn-search-brand-input",
            "yarn-search-sort-input",
            "yarn-search-pagination",
        )
        or any([n_clicks, query_submit, brand_submit])
    )

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

    return update_yarn_search_logic(
        client=client,
        query=query,
        brand=brand,
        sort=sort,
        active_page=page,
        page_size=page_size,
        allow_empty_search=is_user_trigger,
    )


def handle_add_to_stash_logic(
    client: RavelryClient | None,
    yarn_id: int,
    skeins: float | None,
    colorway: str | None,
    dyelot: str | None = None,
    location: str | None = None,
    notes: str | None = None,
    date_added: str | None = None,
    search_results: list[dict[str, Any]] | None = None,
    raw_stash_items: list[dict[str, Any]] | None = None,
    manual_colorway: str | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Process adding a catalog yarn to personal stash either via API or local state fallback.

    Args:
        client: Optional authenticated RavelryClient.
        yarn_id: Unique database ID of the catalog yarn.
        skeins: Skein count.
        colorway: Selected or entered colorway name.
        dyelot: Dye lot string.
        location: Storage location string.
        notes: Personal notes.
        date_added: Purchase or addition date string.
        search_results: Cached yarn search results for metadata lookup.
        raw_stash_items: Current stash item dictionaries in browser store.
        manual_colorway: Optional manual custom colorway override string.

    Returns:
        Tuple of (status_message, updated_stash_items_list).
    """
    raw_stash = list(raw_stash_items) if raw_stash_items else []
    results = search_results or []

    effective_colorway = (
        manual_colorway.strip()
        if manual_colorway and manual_colorway.strip()
        else (colorway.strip() if colorway and colorway.strip() else None)
    )

    # Find matching yarn metadata from search results
    matching_yarn: dict[str, Any] | None = None
    for y in results:
        y_id = y.get("id") if isinstance(y, dict) else getattr(y, "id", None)
        if y_id == yarn_id:
            matching_yarn = y if isinstance(y, dict) else y.model_dump()
            break

    yarn_name = (
        matching_yarn.get("name")
        if matching_yarn
        else f"Yarn #{yarn_id}"
    )
    brand_name = (
        matching_yarn.get("yarn_company_name")
        if matching_yarn
        else ""
    )
    display_title = (
        f"{brand_name} {yarn_name}".strip()
        if brand_name
        else yarn_name
    )

    # 1. Online API call if client is available
    if client is not None:
        try:
            created_item = client.create_stash_item(
                yarn_id=yarn_id,
                skeins=skeins or 1.0,
                colorway_name=effective_colorway,
                dye_lot=dyelot,
                location=location,
                notes=notes,
                purchased_date=date_added,
            )
            serialized_new = (
                created_item.model_dump()
                if hasattr(created_item, "model_dump")
                else created_item
            )
            updated_stash = [serialized_new] + raw_stash
            return (
                f"✓ Successfully added '{display_title}' to your Ravelry stash!",
                updated_stash,
            )
        except Exception as exc:
            logger.warning(
                "Failed to add stash item via API, falling back to local store: %s",
                exc,
            )

    # 2. Local fallback if offline or API call failed
    yardage = matching_yarn.get("yardage") if matching_yarn else None
    grams = matching_yarn.get("grams") if matching_yarn else None
    sk = float(skeins or 1.0)
    total_yards = (float(yardage) * sk) if yardage else None
    total_grams = (float(grams) * sk) if grams else None

    # Generate synthetic ID
    synthetic_id = (
        max([it.get("id", 0) for it in raw_stash if isinstance(it, dict)] or [0])
        + 1001
    )

    new_stash_item: dict[str, Any] = {
        "id": synthetic_id,
        "name": display_title,
        "permalink": matching_yarn.get("permalink", f"stash-{synthetic_id}") if matching_yarn else f"stash-{synthetic_id}",
        "colorway_name": effective_colorway,
        "dye_lot": dyelot,
        "location": location,
        "notes": notes,
        "created_at": date_added or datetime.now(tz=UTC).strftime("%Y-%m-%d"),
        "skeins": sk,
        "total_yards": total_yards,
        "total_grams": total_grams,
        "total_meters": round(total_yards * 0.9144, 2) if total_yards else None,
        "stash_status": {"id": 1, "name": "In stash"},
        "yarn": {
            "id": yarn_id,
            "name": yarn_name,
            "yarn_company_name": brand_name,
            "yarn_weight": matching_yarn.get("yarn_weight") if matching_yarn else None,
            "photos": matching_yarn.get("photos", []) if matching_yarn else [],
        },
        "packs": [
            {
                "id": synthetic_id + 5000,
                "stash_id": synthetic_id,
                "yarn_id": yarn_id,
                "colorway": effective_colorway,
                "dye_lot": dyelot,
                "skeins": sk,
                "total_yards": total_yards,
                "total_grams": total_grams,
                "purchased_date": date_added,
            }
        ],
    }

    updated_stash = [new_stash_item] + raw_stash
    return (
        f"✓ Successfully added '{display_title}' to your local stash!",
        updated_stash,
    )


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
        prevent_initial_call=False,
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
        Output({"type": "stash-status-msg", "index": ALL}, "children"),
        Output("stash-raw-store", "data", allow_duplicate=True),
        Input({"type": "stash-submit-btn", "index": ALL}, "n_clicks"),
        State({"type": "stash-skeins", "index": ALL}, "value"),
        State({"type": "stash-colorway", "index": ALL}, "value"),
        State({"type": "stash-colorway-manual", "index": ALL}, "value"),
        State({"type": "stash-dyelot", "index": ALL}, "value"),
        State({"type": "stash-location", "index": ALL}, "value"),
        State({"type": "stash-notes", "index": ALL}, "value"),
        State({"type": "stash-date-added", "index": ALL}, "value"),
        State({"type": "stash-submit-btn", "index": ALL}, "id"),
        State("yarn-search-results-store", "data"),
        State("stash-raw-store", "data"),
        prevent_initial_call=True,
    )
    def handle_add_to_stash(
        n_clicks_list: list[int | None],
        skeins_list: list[float | None],
        colorway_list: list[str | None],
        manual_colorway_list: list[str | None],
        dyelot_list: list[str | None],
        location_list: list[str | None],
        notes_list: list[str | None],
        date_added_list: list[str | None],
        btn_ids: list[dict[str, Any]],
        search_results: list[dict[str, Any]] | None,
        raw_stash_items: list[dict[str, Any]] | None,
    ) -> tuple[list[Any], list[dict[str, Any]]]:
        if not n_clicks_list or not any(n_clicks_list):
            raise dash.exceptions.PreventUpdate

        triggered_id = ctx.triggered_id
        if not isinstance(triggered_id, dict):
            raise dash.exceptions.PreventUpdate

        clicked_yarn_id = triggered_id.get("index")
        target_idx = None
        for i, bid in enumerate(btn_ids):
            if isinstance(bid, dict) and bid.get("index") == clicked_yarn_id:
                target_idx = i
                break

        if target_idx is None or not n_clicks_list[target_idx]:
            raise dash.exceptions.PreventUpdate

        client = getattr(app, "client", None)
        status_msg, updated_stash = handle_add_to_stash_logic(
            client=client,
            yarn_id=int(clicked_yarn_id),
            skeins=skeins_list[target_idx],
            colorway=colorway_list[target_idx],
            manual_colorway=manual_colorway_list[target_idx] if manual_colorway_list and target_idx < len(manual_colorway_list) else None,
            dyelot=dyelot_list[target_idx],
            location=location_list[target_idx],
            notes=notes_list[target_idx],
            date_added=date_added_list[target_idx],
            search_results=search_results,
            raw_stash_items=raw_stash_items,
        )

        messages = [dash.no_update] * len(btn_ids)
        messages[target_idx] = status_msg
        return messages, updated_stash
