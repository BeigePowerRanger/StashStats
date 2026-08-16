"""Yarn Search page layout with search form, accordion results list, and pagination controls."""

from typing import Any

import dash_bootstrap_components as dbc
from dash import dcc, html

from stashstats.models.yarn import YarnSearchResult
from stashstats.web.components.search import (
    create_yarn_search_accordion,
    create_yarn_search_form,
    create_yarn_search_pagination,
)


def create_yarn_search_layout(
    yarns: list[YarnSearchResult] | list[dict[str, Any]] | None = None,
    page: int = 1,
    total_pages: int = 1,
    total_results: int = 0,
    query: str = "",
    brand: str = "",
) -> dbc.Container:
    """Create the Yarn Search interface layout.

    Args:
        yarns: Optional list of YarnSearchResult objects or dict payloads.
        page: Current active page number (1-indexed).
        total_pages: Total number of pages available.
        total_results: Total count of matched yarns.
        query: Initial search query string.
        brand: Initial brand filter string.

    Returns:
        Configured dbc.Container component.
    """
    raw_yarns = yarns or []

    # 1. Search form row
    search_form = create_yarn_search_form(query=query, brand=brand)

    # 2. Results accordion container with loading spinner
    accordion_component = create_yarn_search_accordion(raw_yarns)
    list_container = dbc.Spinner(
        html.Div(
            accordion_component,
            id="yarn-search-list-container",
            className="yarn-search-results-wrapper",
        ),
        color="primary",
        type="border",
        size="md",
    )

    # 3. Pagination container
    pagination_container = create_yarn_search_pagination(
        page=page,
        total_pages=total_pages,
        total_results=total_results,
    )

    # 4. Data Stores
    serialized_yarns = [
        y.model_dump() if hasattr(y, "model_dump") else y
        for y in raw_yarns
    ]

    stores = [
        dcc.Store(id="yarn-search-results-store", data=serialized_yarns),
        dcc.Store(
            id="yarn-search-paginator-store",
            data={
                "page": page,
                "total_pages": total_pages,
                "total_results": total_results,
                "query": query,
                "brand": brand,
            },
        ),
    ]

    return dbc.Container(
        [
            *stores,
            search_form,
            list_container,
            pagination_container,
        ],
        fluid=True,
        id="yarn-search-container",
        className="p-0",
    )


# Alias for convenience
create_search_layout = create_yarn_search_layout
