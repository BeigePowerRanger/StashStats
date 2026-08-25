"""UI KPI cards and interactive filter components for Stash Analytics dashboard."""

import dash_bootstrap_components as dbc
from dash import dcc, html


def create_kpi_summary_cards(
    total_yards: float = 0.0,
    total_skeins: float = 0.0,
    total_items: int = 0,
    monthly_burn_rate: float = 0.0,
    months_remaining: float | None = None,
) -> dbc.Row:
    """Create a row of summary metric KPI cards.

    Args:
        total_yards: Current active stash yardage.
        total_skeins: Current active skein count.
        total_items: Total count of active stash items.
        monthly_burn_rate: Estimated monthly consumption rate in yards.
        months_remaining: Projected lifespan in months.

    Returns:
        dbc.Row containing structured KPI cards.
    """
    horizon_text = (
        f"{months_remaining:,.1f} mo"
        if months_remaining is not None
        else "Stable / No burn"
    )
    horizon_subtext = (
        f"~{(months_remaining / 12.0):,.1f} years"
        if months_remaining is not None
        else "Infinite horizon"
    )

    card_style = {
        "backgroundColor": "#2b3035",
        "border": "1px solid #3e444c",
        "borderRadius": "8px",
    }

    return dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H6("Active Stash Yardage", className="card-subtitle text-muted mb-1"),
                            html.H3(f"{total_yards:,.0f} yds", className="card-title text-success mb-1"),
                            html.Small(f"{total_skeins:,.1f} skeins in {total_items} items", className="text-secondary"),
                        ]
                    ),
                    style=card_style,
                    className="h-100 shadow-sm",
                ),
                xs=12,
                sm=6,
                lg=3,
                className="mb-3",
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H6("Knitting Velocity", className="card-subtitle text-muted mb-1"),
                            html.H3(f"{monthly_burn_rate:,.1f} yds/mo", className="card-title text-info mb-1"),
                            html.Small(f"~{(monthly_burn_rate / 30.4375):,.1f} yds / day", className="text-secondary"),
                        ]
                    ),
                    style=card_style,
                    className="h-100 shadow-sm",
                ),
                xs=12,
                sm=6,
                lg=3,
                className="mb-3",
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H6("Stash Lifespan Horizon", className="card-subtitle text-muted mb-1"),
                            html.H3(horizon_text, className="card-title text-warning mb-1"),
                            html.Small(horizon_subtext, className="text-secondary"),
                        ]
                    ),
                    style=card_style,
                    className="h-100 shadow-sm",
                ),
                xs=12,
                sm=6,
                lg=3,
                className="mb-3",
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H6("Inventory Utilization", className="card-subtitle text-muted mb-1"),
                            html.H3(
                                f"{total_items} items",
                                className="card-title text-primary mb-1",
                            ),
                            html.Small("Tracked in local cache", className="text-secondary"),
                        ]
                    ),
                    style=card_style,
                    className="h-100 shadow-sm",
                ),
                xs=12,
                sm=6,
                lg=3,
                className="mb-3",
            ),
        ],
        id="analytics-kpi-row",
        className="mb-3",
    )


def create_analytics_filter_bar(
    yarn_weights: list[str] | None = None,
    color_families: list[str] | None = None,
) -> dbc.Card:
    """Create interactive filter controls for the analytics dashboard.

    Args:
        yarn_weights: Optional list of yarn weight options.
        color_families: Optional list of color family options.

    Returns:
        dbc.Card containing interactive filter inputs.
    """
    weight_options = [{"label": w, "value": w} for w in (yarn_weights or [])]
    color_options = [{"label": c, "value": c} for c in (color_families or [])]

    return dbc.Card(
        dbc.CardBody(
            [
                # Row 1: Weight, Color, Search, and Reset
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Filter by Yarn Weight", className="small text-muted mb-1"),
                                dcc.Dropdown(
                                    id="analytics-filter-weight",
                                    options=weight_options,
                                    multi=True,
                                    placeholder="All yarn weights...",
                                    className="dash-bootstrap",
                                    style={"color": "#222"},
                                ),
                            ],
                            xs=12,
                            md=4,
                            className="mb-2 mb-md-0",
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Filter by Color Family", className="small text-muted mb-1"),
                                dcc.Dropdown(
                                    id="analytics-filter-color",
                                    options=color_options,
                                    multi=True,
                                    placeholder="All color families...",
                                    className="dash-bootstrap",
                                    style={"color": "#222"},
                                ),
                            ],
                            xs=12,
                            md=4,
                            className="mb-2 mb-md-0",
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Search / Filter Stash", className="small text-muted mb-1"),
                                dbc.Input(
                                    id="analytics-filter-search",
                                    placeholder="Filter by yarn or brand name...",
                                    type="text",
                                    className="bg-dark text-light border-secondary",
                                ),
                            ],
                            xs=12,
                            md=3,
                            className="mb-2 mb-md-0",
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Reset", className="small text-muted mb-1 invisible d-none d-md-block"),
                                dbc.Button(
                                    "Reset",
                                    id="analytics-filter-reset",
                                    color="secondary",
                                    outline=True,
                                    className="w-100",
                                ),
                            ],
                            xs=12,
                            md=1,
                            className="d-flex align-items-end",
                        ),
                    ],
                    align="center",
                    className="mb-3",
                ),
                # Row 2: Quantity Filters (Grams, Yards, Meters, Skeins)
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Grams (Min / Max)", className="small text-muted mb-1"),
                                dbc.InputGroup(
                                    [
                                        dbc.Input(
                                            id="analytics-filter-min-grams",
                                            type="number",
                                            placeholder="Min g",
                                            min=0,
                                            className="bg-dark text-light border-secondary",
                                        ),
                                        dbc.InputGroupText("-", className="bg-dark text-muted border-secondary"),
                                        dbc.Input(
                                            id="analytics-filter-max-grams",
                                            type="number",
                                            placeholder="Max g",
                                            min=0,
                                            className="bg-dark text-light border-secondary",
                                        ),
                                    ],
                                    size="sm",
                                ),
                            ],
                            xs=12,
                            sm=6,
                            md=3,
                            className="mb-2 mb-md-0",
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Yards (Min / Max)", className="small text-muted mb-1"),
                                dbc.InputGroup(
                                    [
                                        dbc.Input(
                                            id="analytics-filter-min-yards",
                                            type="number",
                                            placeholder="Min yd",
                                            min=0,
                                            className="bg-dark text-light border-secondary",
                                        ),
                                        dbc.InputGroupText("-", className="bg-dark text-muted border-secondary"),
                                        dbc.Input(
                                            id="analytics-filter-max-yards",
                                            type="number",
                                            placeholder="Max yd",
                                            min=0,
                                            className="bg-dark text-light border-secondary",
                                        ),
                                    ],
                                    size="sm",
                                ),
                            ],
                            xs=12,
                            sm=6,
                            md=3,
                            className="mb-2 mb-md-0",
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Meters (Min / Max)", className="small text-muted mb-1"),
                                dbc.InputGroup(
                                    [
                                        dbc.Input(
                                            id="analytics-filter-min-meters",
                                            type="number",
                                            placeholder="Min m",
                                            min=0,
                                            className="bg-dark text-light border-secondary",
                                        ),
                                        dbc.InputGroupText("-", className="bg-dark text-muted border-secondary"),
                                        dbc.Input(
                                            id="analytics-filter-max-meters",
                                            type="number",
                                            placeholder="Max m",
                                            min=0,
                                            className="bg-dark text-light border-secondary",
                                        ),
                                    ],
                                    size="sm",
                                ),
                            ],
                            xs=12,
                            sm=6,
                            md=3,
                            className="mb-2 mb-md-0",
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Skeins (Min / Max)", className="small text-muted mb-1"),
                                dbc.InputGroup(
                                    [
                                        dbc.Input(
                                            id="analytics-filter-min-skeins",
                                            type="number",
                                            placeholder="Min sk",
                                            step=0.1,
                                            min=0,
                                            className="bg-dark text-light border-secondary",
                                        ),
                                        dbc.InputGroupText("-", className="bg-dark text-muted border-secondary"),
                                        dbc.Input(
                                            id="analytics-filter-max-skeins",
                                            type="number",
                                            placeholder="Max sk",
                                            step=0.1,
                                            min=0,
                                            className="bg-dark text-light border-secondary",
                                        ),
                                    ],
                                    size="sm",
                                ),
                            ],
                            xs=12,
                            sm=6,
                            md=3,
                            className="mb-2 mb-md-0",
                        ),
                    ],
                    align="center",
                ),
            ]
        ),
        style={
            "backgroundColor": "#2b3035",
            "border": "1px solid #3e444c",
            "borderRadius": "8px",
        },
        className="mb-4 shadow-sm",
    )
