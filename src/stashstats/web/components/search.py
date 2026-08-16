"""Yarn Search UI components, search forms, and expanding accordion cards."""

from typing import Any

import dash_bootstrap_components as dbc
from dash import html

from stashstats.models.yarn import YarnSearchResult


def create_yarn_search_form(query: str = "", brand: str = "") -> dbc.Row:
    """Render the dual search input form for keyword and brand filters.

    Args:
        query: Initial search keyword string.
        brand: Initial brand / yarn company filter string.

    Returns:
        dbc.Row component containing keyword input, brand input, and search trigger button.
    """
    query_input = dbc.InputGroup(
        [
            dbc.InputGroupText(
                html.I(className="bi bi-search text-muted"),
                className="bg-dark border-secondary",
            ),
            dbc.Input(
                id="yarn-search-query-input",
                type="search",
                placeholder="Search yarn name or keywords...",
                value=query,
                debounce=True,
                className="bg-dark text-light border-secondary",
            ),
        ],
        className="mb-2 mb-md-0",
    )

    brand_input = dbc.InputGroup(
        [
            dbc.InputGroupText(
                html.I(className="bi bi-building text-muted"),
                className="bg-dark border-secondary",
            ),
            dbc.Input(
                id="yarn-search-brand-input",
                type="search",
                placeholder="Filter by brand / company...",
                value=brand,
                debounce=True,
                className="bg-dark text-light border-secondary",
            ),
        ],
        className="mb-2 mb-md-0",
    )

    search_btn = dbc.Button(
        [html.I(className="bi bi-search me-1"), "Search"],
        id="yarn-search-btn",
        color="primary",
        className="fw-semibold d-flex align-items-center justify-content-center w-100",
    )

    return dbc.Row(
        [
            dbc.Col(query_input, xs=12, md=5, lg=5),
            dbc.Col(brand_input, xs=12, md=5, lg=5),
            dbc.Col(search_btn, xs=12, md=2, lg=2),
        ],
        className="mb-3 g-2 align-items-center",
    )


def create_yarn_search_details(yarn: YarnSearchResult | dict[str, Any]) -> html.Div:
    """Render structured technical specifications and attributes in the expanded accordion body.

    Args:
        yarn: YarnSearchResult model or dictionary.

    Returns:
        html.Div component containing spec badges and Ravelry link.
    """
    if not isinstance(yarn, YarnSearchResult):
        yarn = YarnSearchResult.model_validate(yarn)

    specs: list[html.Component] = []

    # 1. Weight & Texture
    weight_name = yarn.yarn_weight.name if yarn.yarn_weight else None
    if weight_name:
        specs.append(
            dbc.Badge(f"Weight: {weight_name}", color="info", pill=True, className="me-2 mb-2 p-2")
        )

    if yarn.texture:
        specs.append(
            dbc.Badge(f"Texture: {yarn.texture}", color="secondary", pill=True, className="me-2 mb-2 p-2")
        )

    wpi = yarn.wpi or (yarn.yarn_weight.wpi if yarn.yarn_weight else None)
    if wpi:
        specs.append(
            dbc.Badge(f"WPI: {wpi}", color="dark", className="border border-secondary me-2 mb-2 p-2 text-light", pill=True)
        )

    # 2. Yardage & Grams
    unit_parts = []
    if yarn.yardage is not None:
        unit_parts.append(f"Yardage: {yarn.yardage:g} yds")
    if yarn.grams is not None:
        unit_parts.append(f"Grams: {yarn.grams:g} g")

    if unit_parts:
        specs.append(
            dbc.Badge(" / ".join(unit_parts), color="dark", className="border border-secondary me-2 mb-2 p-2 text-light", pill=True)
        )

    # 3. Gauge Information
    gauge_text = None
    if yarn.yarn_weight and yarn.yarn_weight.knit_gauge:
        gauge_text = f"Gauge: {yarn.yarn_weight.knit_gauge}"
    elif yarn.min_gauge is not None:
        divisor = yarn.gauge_divisor or 4
        if yarn.max_gauge is not None and yarn.max_gauge != yarn.min_gauge:
            gauge_text = f"Gauge: {yarn.min_gauge:g}-{yarn.max_gauge:g} sts / {divisor} in"
        else:
            gauge_text = f"Gauge: {yarn.min_gauge:g} sts / {divisor} in"

    if gauge_text:
        specs.append(
            dbc.Badge(gauge_text, color="secondary", pill=True, className="me-2 mb-2 p-2")
        )

    # 4. Care & Washability
    if yarn.machine_washable is not None:
        wash_color = "success" if yarn.machine_washable else "warning"
        wash_label = "Machine Washable" if yarn.machine_washable else "Hand Wash Only"
        specs.append(
            dbc.Badge(wash_label, color=wash_color, pill=True, className="me-2 mb-2 p-2")
        )

    # 5. Community Rating
    if yarn.rating_average is not None and yarn.rating_average > 0:
        specs.append(
            dbc.Badge(
                f"{yarn.rating_average:.2f} ★ ({yarn.rating_count or 0} ratings)",
                color="warning",
                pill=True,
                className="text-dark me-2 mb-2 p-2 fw-semibold",
            )
        )

    specs_container = html.Div(specs, className="d-flex flex-wrap align-items-center mb-2")

    # Link button to Ravelry
    link_btn = dbc.Button(
        [html.I(className="bi bi-box-arrow-up-right me-1"), "View on Ravelry"],
        href=f"https://www.ravelry.com/yarns/library/{yarn.permalink}",
        target="_blank",
        color="primary",
        outline=True,
        size="sm",
        className="mt-1 d-inline-flex align-items-center",
    )

    return html.Div(
        [
            specs_container,
            html.Div(link_btn, className="mt-2 pt-2 border-top border-secondary"),
        ],
        className="py-2 px-3 bg-dark text-light",
    )


def create_yarn_search_accordion_item(
    yarn: YarnSearchResult | dict[str, Any],
    index: int = 0,
) -> dbc.AccordionItem:
    """Render a single expandable accordion card item for a yarn search result.

    Args:
        yarn: YarnSearchResult data model or dictionary.
        index: Index for unique item_id.

    Returns:
        Configured dbc.AccordionItem component.
    """
    if not isinstance(yarn, YarnSearchResult):
        yarn = YarnSearchResult.model_validate(yarn)

    # Thumbnail photo
    photo_url = None
    if yarn.first_photo:
        photo_url = (
            yarn.first_photo.square_url
            or yarn.first_photo.small_url
            or yarn.first_photo.thumbnail_url
            or yarn.first_photo.medium_url
        )

    if photo_url:
        thumbnail = html.Img(
            src=photo_url,
            alt=yarn.name,
            style={"width": "35px", "height": "35px", "objectFit": "cover"},
            className="rounded me-2 flex-shrink-0",
        )
    else:
        thumbnail = html.Div(
            html.I(className="bi bi-box-seam text-info"),
            className="d-inline-flex align-items-center justify-content-center bg-secondary rounded me-2 flex-shrink-0",
            style={"width": "35px", "height": "35px"},
        )

    company_name = yarn.yarn_company_name or "Unknown Brand"
    display_title = f"{company_name} — {yarn.name}"
    title_text = html.Span(display_title, className="fw-bold fs-6 text-light me-auto")

    badges: list[html.Component] = []

    if yarn.yarn_weight and yarn.yarn_weight.name:
        badges.append(
            dbc.Badge(
                yarn.yarn_weight.name,
                color="info",
                pill=True,
                className="me-2 px-2 py-1 fs-7 align-self-center",
            )
        )

    if yarn.discontinued:
        badges.append(
            dbc.Badge(
                "Discontinued",
                color="danger",
                pill=True,
                className="me-2 px-2 py-1 fs-7 align-self-center",
            )
        )

    header_title = html.Div(
        [
            thumbnail,
            title_text,
            html.Div(badges, className="d-flex align-items-center ms-auto"),
        ],
        className="d-flex align-items-center w-100 pe-2",
    )

    body = create_yarn_search_details(yarn)

    return dbc.AccordionItem(
        title=header_title,
        item_id=f"yarn-search-item-{yarn.id if yarn.id else index}",
        children=body,
        className="mb-2 border border-secondary rounded overflow-hidden",
    )


def create_yarn_search_accordion(
    yarns: list[YarnSearchResult] | list[dict[str, Any]] | None = None,
) -> html.Div | dbc.Accordion:
    """Render the full collapsible accordion list for yarn search results.

    Args:
        yarns: Optional list of YarnSearchResult objects or dicts.

    Returns:
        dbc.Accordion component with search results or empty state alert.
    """
    if not yarns:
        return html.Div(
            dbc.Alert(
                [
                    html.I(className="bi bi-info-circle me-2"),
                    "No yarns found matching search criteria.",
                ],
                color="info",
                className="text-center my-4",
            ),
            id="yarn-search-empty-state",
        )

    items = [
        create_yarn_search_accordion_item(y, index=i)
        for i, y in enumerate(yarns)
    ]

    return dbc.Accordion(
        items,
        id="yarn-search-accordion",
        start_collapsed=True,
        always_open=True,
        className="mt-2",
    )


def create_yarn_search_pagination(
    page: int = 1,
    total_pages: int = 1,
    total_results: int = 0,
) -> html.Div:
    """Render traditional pagination controls and info for search results.

    Args:
        page: Active page index (1-indexed).
        total_pages: Maximum page count.
        total_results: Total matching records across all pages.

    Returns:
        html.Div container with dbc.Pagination and info text.
    """
    safe_max_page = max(1, total_pages)
    safe_page = max(1, min(page, safe_max_page))

    pagination = dbc.Pagination(
        id="yarn-search-pagination",
        active_page=safe_page,
        max_value=safe_max_page,
        fully_expanded=False,
        previous_next=True,
        first_last=True,
        className="justify-content-center mt-3",
    )

    info_text = f"Showing page {safe_page} of {safe_max_page} ({total_results} yarns found)"
    pagination_info = html.Div(
        info_text,
        id="yarn-search-pagination-info",
        className="text-muted text-center small mt-1",
    )

    return html.Div(
        [
            pagination,
            pagination_info,
        ],
        id="yarn-search-pagination-container",
        className="mt-3 mb-4",
    )
