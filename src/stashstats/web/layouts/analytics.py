"""Stash Analytics dashboard layout with metric cards, interactive filters, and Plotly charts."""

from typing import Any

import dash_bootstrap_components as dbc
from dash import dcc, html

from stashstats.analytics.distributions import StashDistributionSummary
from stashstats.models.analytics import StashVelocityReport
from stashstats.web.components.analytics import (
    create_analytics_filter_bar,
    create_kpi_summary_cards,
)
from stashstats.web.components.analytics_charts import (
    create_fiber_donut_chart,
    create_monthly_flow_chart,
    create_stash_by_time_chart,
    create_velocity_pace_chart,
    create_weight_distribution_chart,
)


def create_analytics_layout(
    report: StashVelocityReport | None = None,
    distribution: StashDistributionSummary | None = None,
    yarn_weights: list[str] | None = None,
    color_families: list[str] | None = None,
) -> dbc.Container:
    """Create the full Stash Analytics dashboard tab layout.

    Args:
        report: Optional pre-computed StashVelocityReport.
        distribution: Optional pre-computed StashDistributionSummary.
        yarn_weights: Optional list of yarn weight filter choices.
        color_families: Optional list of color family filter choices.

    Returns:
        Configured dbc.Container with complete analytics dashboard UI.
    """
    total_yards = report.total_active_yards if report else 0.0
    total_skeins = report.total_active_skeins if report else 0.0
    total_items = report.total_active_items if report else 0
    monthly_burn_rate = (
        report.horizon.monthly_burn_rate_yards if report and report.horizon else 0.0
    )
    months_remaining = (
        report.horizon.months_remaining if report and report.horizon else None
    )

    kpi_cards = create_kpi_summary_cards(
        total_yards=total_yards,
        total_skeins=total_skeins,
        total_items=total_items,
        monthly_burn_rate=monthly_burn_rate,
        months_remaining=months_remaining,
    )

    resolved_weights = (
        yarn_weights
        or ([w.name for w in distribution.weights] if distribution else [])
    )
    resolved_colors = (
        color_families
        or ([c.name for c in distribution.color_families] if distribution else [])
    )

    filter_bar = create_analytics_filter_bar(
        yarn_weights=resolved_weights,
        color_families=resolved_colors,
    )

    fiber_fig = create_fiber_donut_chart(distribution.fibers if distribution else [])
    weight_fig = create_weight_distribution_chart(
        distribution.weights if distribution else []
    )
    timeline_fig = create_stash_by_time_chart(
        rollups=report.periodic_monthly if report else None
    )
    flow_fig = create_monthly_flow_chart(report.periodic_monthly if report else [])
    velocity_fig = create_velocity_pace_chart(
        velocity_30d=report.velocity_30d if report else None,
        velocity_90d=report.velocity_90d if report else None,
        velocity_365d=report.velocity_365d if report else None,
    )

    card_container_style = {
        "backgroundColor": "#2b3035",
        "border": "1px solid #3e444c",
        "borderRadius": "8px",
    }

    charts_row_1 = dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H5(
                                "Stash Inventory Over Time",
                                className="m-0 text-light fs-6 fw-bold",
                            ),
                            className="bg-transparent border-secondary",
                        ),
                        dbc.CardBody(
                            dcc.Loading(
                                dcc.Graph(
                                    id="analytics-timeline-chart",
                                    figure=timeline_fig,
                                    config={"displayModeBar": False, "responsive": True},
                                ),
                                type="circle",
                                color="#00bc8c",
                            )
                        ),
                    ],
                    style=card_container_style,
                    className="h-100 shadow-sm",
                ),
                xs=12,
                className="mb-4",
            ),
        ]
    )

    charts_row_2 = dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H5(
                                "Fiber Composition Breakdown",
                                className="m-0 text-light fs-6 fw-bold",
                            ),
                            className="bg-transparent border-secondary",
                        ),
                        dbc.CardBody(
                            dcc.Loading(
                                dcc.Graph(
                                    id="analytics-fiber-chart",
                                    figure=fiber_fig,
                                    config={"displayModeBar": False, "responsive": True},
                                ),
                                type="circle",
                                color="#00bc8c",
                            )
                        ),
                    ],
                    style=card_container_style,
                    className="h-100 shadow-sm",
                ),
                xs=12,
                lg=6,
                className="mb-4",
            ),
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H5(
                                "Yarn Weight Distribution",
                                className="m-0 text-light fs-6 fw-bold",
                            ),
                            className="bg-transparent border-secondary",
                        ),
                        dbc.CardBody(
                            dcc.Loading(
                                dcc.Graph(
                                    id="analytics-weight-chart",
                                    figure=weight_fig,
                                    config={"displayModeBar": False, "responsive": True},
                                ),
                                type="circle",
                                color="#00bc8c",
                            )
                        ),
                    ],
                    style=card_container_style,
                    className="h-100 shadow-sm",
                ),
                xs=12,
                lg=6,
                className="mb-4",
            ),
        ]
    )

    charts_row_3 = dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H5(
                                "Monthly Stash Flow (Acquisitions vs Consumption)",
                                className="m-0 text-light fs-6 fw-bold",
                            ),
                            className="bg-transparent border-secondary",
                        ),
                        dbc.CardBody(
                            dcc.Loading(
                                dcc.Graph(
                                    id="analytics-flow-chart",
                                    figure=flow_fig,
                                    config={"displayModeBar": False, "responsive": True},
                                ),
                                type="circle",
                                color="#00bc8c",
                            )
                        ),
                    ],
                    style=card_container_style,
                    className="h-100 shadow-sm",
                ),
                xs=12,
                lg=6,
                className="mb-4",
            ),
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H5(
                                "Consumption Velocity Horizons",
                                className="m-0 text-light fs-6 fw-bold",
                            ),
                            className="bg-transparent border-secondary",
                        ),
                        dbc.CardBody(
                            dcc.Loading(
                                dcc.Graph(
                                    id="analytics-velocity-chart",
                                    figure=velocity_fig,
                                    config={"displayModeBar": False, "responsive": True},
                                ),
                                type="circle",
                                color="#00bc8c",
                            )
                        ),
                    ],
                    style=card_container_style,
                    className="h-100 shadow-sm",
                ),
                xs=12,
                lg=6,
                className="mb-4",
            ),
        ]
    )

    return dbc.Container(
        [
            html.Div(
                [
                    html.H4("Stash Analytics & Consumption Velocity", className="text-light fw-bold mb-1"),
                    html.P("Real-time inventory breakdowns, timeline trends, net flow history, and projected depletion horizons.", className="text-muted small mb-3"),
                ],
                className="mb-3",
            ),
            html.Div(kpi_cards, id="analytics-kpi-container"),
            filter_bar,
            charts_row_1,
            charts_row_2,
            charts_row_3,
        ],
        id="analytics-container",
        fluid=True,
        className="p-0",
    )
