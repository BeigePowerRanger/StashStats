"""Yarn Search UI components, search forms, and expanding accordion cards."""

from datetime import UTC, datetime
from typing import Any

import dash_bootstrap_components as dbc
from dash import dcc, html

from stashstats.models.yarn import YarnSearchResult

SEARCH_CATEGORIES: list[dict[str, str]] = [
    {"label": "Yarns", "value": "yarns"},
    {"label": "Yarn Companies", "value": "yarn_companies"},
    {"label": "Personal Stash", "value": "personal_stash"},
    {"label": "Projects", "value": "projects"},
    {"label": "Patterns", "value": "patterns"},
]

SORT_CATEGORIES: list[dict[str, str]] = [
    {"label": "Best Match", "value": "best_match"},
    {"label": "Highest Rating", "value": "highest_rating"},
    {"label": "Most Projects", "value": "most_projects"},
]

DEFAULT_SEARCH_CATEGORY = "yarns"
DEFAULT_SORT_CATEGORY = "best_match"

DARK_INPUT_STYLE = {"backgroundColor": "#333", "color": "#fff", "border": "1px solid #555"}
DARK_LABEL_STYLE = {"backgroundColor": "#444", "color": "#ccc", "border": "1px solid #555"}


def create_yarn_search_form(
    query: str = "",
    brand: str = "",
    category: str = DEFAULT_SEARCH_CATEGORY,
    sort: str = DEFAULT_SORT_CATEGORY,
) -> dbc.Row:
    """Render the search input form with category, query, sort, and submit button.

    Args:
        query: Initial search keyword string.
        brand: Initial brand / yarn company filter string.
        category: Selected search category.
        sort: Selected sort order.

    Returns:
        dbc.Row component containing category select, query input, sort select, and submit button.
    """
    category_input = dbc.InputGroup(
        [
            dbc.InputGroupText("Category", style=DARK_LABEL_STYLE),
            dbc.Select(
                id="yarn-search-category-input",
                options=SEARCH_CATEGORIES,
                value=category or DEFAULT_SEARCH_CATEGORY,
                placeholder="Select Category",
                style=DARK_INPUT_STYLE,
            ),
        ],
        className="mb-2 mb-sm-0",
    )

    query_input = dbc.InputGroup(
        [
            dbc.InputGroupText("Search", style=DARK_LABEL_STYLE),
            dbc.Input(
                id="yarn-search-query-input",
                type="search",
                placeholder="Flux Capacitor",
                value=query,
                debounce=True,
                style=DARK_INPUT_STYLE,
            ),
        ],
        className="mb-2 mb-sm-0",
    )

    brand_input = dbc.InputGroup(
        [
            dbc.InputGroupText("Brand", style=DARK_LABEL_STYLE),
            dbc.Input(
                id="yarn-search-brand-input",
                type="search",
                placeholder="Filter by brand...",
                value=brand,
                debounce=True,
                style=DARK_INPUT_STYLE,
            ),
        ],
        className="mb-2 mb-sm-0",
    )

    sort_input = dbc.InputGroup(
        [
            dbc.InputGroupText("Sort", style=DARK_LABEL_STYLE),
            dbc.Select(
                id="yarn-search-sort-input",
                options=SORT_CATEGORIES,
                value=sort or DEFAULT_SORT_CATEGORY,
                placeholder="Select Sort",
                style=DARK_INPUT_STYLE,
            ),
        ],
        className="mb-2 mb-sm-0",
    )

    search_btn = dbc.Button(
        "Submit",
        id="yarn-search-btn",
        color="primary",
        className="w-100 w-sm-auto fw-semibold",
    )

    return dbc.Row(
        [
            dbc.Col(category_input, xs=12, sm="auto"),
            dbc.Col(query_input, xs=12, sm="auto"),
            dbc.Col(brand_input, xs=12, sm="auto"),
            dbc.Col(sort_input, xs=12, sm="auto"),
            dbc.Col(search_btn, xs=12, sm="auto"),
            html.Hr(style={"margin": "20px 0"}),
        ],
        className="mb-3 g-2 align-items-center",
    )


def create_yarn_search_details(
    yarn: YarnSearchResult | dict[str, Any],
) -> html.Div:
    """Render structured technical specifications, colorway badges, and inline stash form.

    Args:
        yarn: YarnSearchResult model or dictionary.

    Returns:
        html.Div component containing specs, colorway badges, and stash form.
    """
    if not isinstance(yarn, YarnSearchResult):
        yarn = YarnSearchResult.model_validate(yarn)

    yarn_id = yarn.id or 0
    company = yarn.yarn_company_name or ""
    grams = yarn.grams
    yardage = yarn.yardage
    discontinued = yarn.discontinued
    machine_washable = yarn.machine_washable
    colorways = getattr(yarn, "colorways", None) or []

    # 1. Specs
    specs: list[html.Component] = []
    if company and company.strip():
        specs.append(html.P(html.Strong(f"Company: {company}")))

    if yarn.yarn_weight and yarn.yarn_weight.name:
        specs.append(html.P(f"Weight: {yarn.yarn_weight.name}"))
    elif grams is not None:
        specs.append(
            html.P(f"Weight: {grams:g}g" if isinstance(grams, (int, float)) else f"Weight: {grams}g")
        )

    if yardage is not None:
        specs.append(
            html.P(
                f"Yardage: {yardage:g} yards"
                if isinstance(yardage, (int, float))
                else f"Yardage: {yardage} yards"
            )
        )

    if discontinued is not None:
        specs.append(html.P(f"Discontinued: {'Yes' if discontinued else 'No'}"))

    if machine_washable is not None:
        specs.append(html.P(f"Machine Washable: {'Yes' if machine_washable else 'No'}"))

    if yarn.texture:
        specs.append(html.P(f"Texture: {yarn.texture}"))

    if yarn.rating_average is not None and yarn.rating_average > 0:
        specs.append(html.P(f"Rating: {yarn.rating_average:.2f} ★ ({yarn.rating_count or 0} ratings)"))

    if yarn.permalink:
        link_btn = dbc.Button(
            [html.I(className="bi bi-box-arrow-up-right me-1"), "View on Ravelry"],
            href=f"https://www.ravelry.com/yarns/library/{yarn.permalink}",
            target="_blank",
            color="primary",
            outline=True,
            size="sm",
            className="mt-1 mb-2 d-inline-flex align-items-center",
        )
        specs.append(link_btn)

    # 2. Colorways
    colorway_components: list[html.Component] = []
    if colorways:
        colorway_components.append(html.Strong("Colorways:"))
        colorway_components.append(
            html.Div(
                [
                    dbc.Badge(c, color="secondary", className="me-1 mb-1")
                    for c in colorways
                ],
                style={"flexWrap": "wrap", "display": "flex", "marginTop": "5px"},
            )
        )

    # 3. Inline Add to Stash Form
    colorway_options = [{"label": c, "value": c} for c in colorways] if colorways else []
    stash_form = html.Div(
        [
            html.Hr(),
            html.H6("Add to Stash", className="text-primary"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Skeins"),
                            dbc.Input(
                                type="number",
                                id={"type": "stash-skeins", "index": yarn_id},
                                placeholder="1.0",
                                min=0,
                                step=0.1,
                                style=DARK_INPUT_STYLE,
                            ),
                        ],
                        xs=12,
                        sm=4,
                        className="mb-2 mb-sm-0",
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Colorway"),
                            dbc.Select(
                                id={"type": "stash-colorway", "index": yarn_id},
                                options=colorway_options,
                                placeholder="Select or leave blank",
                                style=DARK_INPUT_STYLE,
                            )
                            if colorways
                            else dbc.Input(
                                type="text",
                                id={"type": "stash-colorway", "index": yarn_id},
                                placeholder="Colorway name",
                                style=DARK_INPUT_STYLE,
                            ),
                        ],
                        xs=12,
                        sm=4,
                        className="mb-2 mb-sm-0",
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Dye Lot"),
                            dbc.Input(
                                type="text",
                                id={"type": "stash-dyelot", "index": yarn_id},
                                placeholder="e.g. 42",
                                style=DARK_INPUT_STYLE,
                            ),
                        ],
                        xs=12,
                        sm=4,
                    ),
                ],
                className="mb-2",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Location"),
                            dbc.Input(
                                type="text",
                                id={"type": "stash-location", "index": yarn_id},
                                placeholder="e.g. Closet",
                                style=DARK_INPUT_STYLE,
                            ),
                        ],
                        xs=12,
                        sm=6,
                        className="mb-2 mb-sm-0",
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Notes"),
                            dbc.Input(
                                type="text",
                                id={"type": "stash-notes", "index": yarn_id},
                                placeholder="e.g. soft texture",
                                style=DARK_INPUT_STYLE,
                            ),
                        ],
                        xs=12,
                        sm=6,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Date Added"),
                            html.Br(),
                            dcc.DatePickerSingle(
                                id={"type": "stash-date-added", "index": yarn_id},
                                date=datetime.now(tz=UTC).date().isoformat(),
                                display_format="YYYY-MM-DD",
                                className="w-100",
                            ),
                        ],
                        xs=12,
                    )
                ],
                className="mb-3",
            ),
            dbc.Button(
                "Add Yarn to Stash",
                id={"type": "stash-submit-btn", "index": yarn_id},
                color="success",
                size="sm",
                className="w-100",
            ),
            html.Div(id={"type": "stash-status-msg", "index": yarn_id}, className="mt-2 text-info"),
        ],
        style={
            "padding": "10px",
            "border": "1px solid #444",
            "borderRadius": "5px",
            "backgroundColor": "#222",
            "marginTop": "15px",
        },
    )

    return html.Div(
        specs + colorway_components + [stash_form],
        className="yarn-search-details py-2",
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

    company_name = yarn.yarn_company_name or ""
    title = f"{company_name} — {yarn.name}" if company_name and company_name.strip() else yarn.name
    yarn_id = yarn.id if yarn.id else index

    body_details = create_yarn_search_details(yarn)

    labels_col = dbc.Col(
        body_details,
        xs=12,
        md=8,
    )

    # Photo Carousel or Image (150px height)
    photos: list[str] = []
    if getattr(yarn, "photos", None) and yarn.photos:
        photos = [
            str(p.medium_url or p.square_url or p.small_url or p.thumbnail_url)
            for p in yarn.photos
            if (p.medium_url or p.square_url or p.small_url or p.thumbnail_url)
        ]
    elif getattr(yarn, "first_photo", None) and yarn.first_photo:
        fp = yarn.first_photo
        fp_url = fp.medium_url or fp.square_url or fp.small_url or fp.thumbnail_url
        if fp_url:
            photos = [str(fp_url)]

    if photos and len(photos) > 1:
        carousel_items = [{"key": str(i), "src": str(url)} for i, url in enumerate(photos)]
        img_element: html.Component = dbc.Carousel(
            items=carousel_items,
            controls=True,
            indicators=True,
            interval=None,
            style={
                "height": "150px",
                "width": "150px",
                "margin": "10px",
                "borderRadius": "8px",
                "overflow": "hidden",
            },
        )
    elif photos:
        img_element = html.Img(
            src=str(photos[0]),
            alt=yarn.name,
            style={
                "height": "150px",
                "width": "auto",
                "maxWidth": "100%",
                "objectFit": "cover",
                "margin": "10px",
                "borderRadius": "8px",
            },
        )
    else:
        img_element = html.Div(
            html.I(className="bi bi-box-seam text-info fs-1"),
            className="d-flex align-items-center justify-content-center bg-dark border border-secondary rounded",
            style={"height": "150px", "width": "150px", "margin": "10px"},
        )

    thumbnail_col = dbc.Col(
        [img_element] if img_element is not None else [],
        xs=12,
        md=4,
        className="d-flex align-items-center justify-content-center",
    )

    return dbc.AccordionItem(
        dbc.Row(
            [labels_col, thumbnail_col],
        ),
        title=title,
        item_id=f"yarn-search-item-{yarn_id}",
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
