"""Reactive callbacks for Yarn Search form inputs, API search execution, and pagination."""

import logging
from typing import Any

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, ctx, html

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


def update_yarn_search_logic(
    client: RavelryClient | None,
    query: str | None,
    brand: str | None,
    active_page: int | None = 1,
    page_size: int = 25,
) -> tuple[Any, int, int, str, list[dict[str, Any]], dict[str, Any]]:
    """Execute yarn search against Ravelry API and format UI results.

    Args:
        client: Authenticated RavelryClient instance (or None if offline).
        query: Search keyword string.
        brand: Brand name filter string.
        active_page: Target page number (1-indexed).
        page_size: Results per page count.

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

    # Empty inputs or missing client -> return empty search state
    if not search_str or client is None:
        accordion = create_yarn_search_accordion([])
        return (
            accordion,
            1,
            1,
            "Showing page 1 of 1 (0 yarns found)",
            [],
            {
                "page": 1,
                "total_pages": 1,
                "total_results": 0,
                "query": clean_query,
                "brand": clean_brand,
            },
        )

    page_num = max(1, active_page) if active_page is not None else 1

    try:
        response = client.search_yarns(
            query=search_str,
            page=page_num,
            page_size=page_size,
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
            },
        )


def handle_yarn_search_callback(
    client: RavelryClient | None,
    triggered_id: Any,
    n_clicks: int | None,
    query_submit: int | None,
    brand_submit: int | None,
    active_page: int | None,
    query_val: str | None,
    brand_val: str | None,
    paginator_store: dict[str, Any] | None,
    page_size: int = 25,
) -> tuple[Any, int, int, str, list[dict[str, Any]], dict[str, Any]]:
    """Parse trigger sources, determine target query/page, and run search.

    Args:
        client: Authenticated RavelryClient instance.
        triggered_id: ID of the Dash component that fired callback.
        n_clicks: Search button click count.
        query_submit: Enter keypress count on query input.
        brand_submit: Enter keypress count on brand input.
        active_page: Current or requested pagination page.
        query_val: Search input text value.
        brand_val: Brand input text value.
        paginator_store: Previous search paginator metadata dictionary.
        page_size: Result count per page.

    Returns:
        Formatted 6-tuple matching update_yarn_search_logic.
    """
    if not triggered_id and not any([n_clicks, query_submit, brand_submit, active_page]):
        raise dash.exceptions.PreventUpdate

    if triggered_id == "yarn-search-pagination":
        # Pagination click -> preserve previous search query/brand from store
        query = (paginator_store or {}).get("query", query_val)
        brand = (paginator_store or {}).get("brand", brand_val)
        page = active_page or 1
    else:
        # Search button or Enter submit -> new search starting at page 1
        query = query_val
        brand = brand_val
        page = 1

    return update_yarn_search_logic(
        client=client,
        query=query,
        brand=brand,
        active_page=page,
        page_size=page_size,
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
            active_page=active_page,
            query_val=query_val,
            brand_val=brand_val,
            paginator_store=paginator_store,
        )
