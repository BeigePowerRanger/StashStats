"""Stash Analytics dashboard layout with metric cards, unit metric toggle, and Plotly charts."""

from typing import Any

import dash_bootstrap_components as dbc
from dash import dcc, html

from stashstats.analytics.distributions import StashDistributionSummary
from stashstats.models.analytics import ProjectUsageRecord, StashVelocityReport
from stashstats.web.components.analytics import (
    create_kpi_summary_cards,
    create_unit_selector_bar,
)
from stashstats.web.components.analytics_charts import (
    create_fiber_donut_chart,
    create_monthly_flow_chart,
    create_projects_pie_chart,
    create_stash_by_time_chart,
    create_weight_distribution_chart,
)


def create_analytics_layout(
    report: StashVelocityReport | None = None,
    distribution: StashDistributionSummary | None = None,
    project_usages: list[ProjectUsageRecord] | None = None,
    unit: str = "yards",
    **kwargs: Any,
) -> dbc.Container:
    """Create the full Stash Analytics dashboard tab layout.

    Args:
        report: Optional pre-computed StashVelocityReport.
        distribution: Optional pre-computed StashDistributionSummary.
        project_usages: Optional pre-computed list of ProjectUsageRecord.
        unit: Initial selected metric unit ('yards', 'meters', 'grams', 'skeins').

    Returns:
        Configured dbc.Container with complete analytics dashboard UI.
    """
    total_yards = report.total_active_yards if report else 0.0
    total_meters = total_yards * 0.9144
    total_grams = (
        sum(w.total_grams for w in distribution.weights)
        if distribution and distribution.weights
        else total_yards * 0.45
    )
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
        total_meters=total_meters,
        total_grams=total_grams,
        total_skeins=total_skeins,
        total_items=total_items,
        monthly_burn_rate=monthly_burn_rate,
        months_remaining=months_remaining,
        unit=unit,
    )

    unit_bar = create_unit_selector_bar(active_unit=unit)

    fiber_fig = create_fiber_donut_chart(
        distribution.fibers if distribution else [],
        unit=unit,
    )
    weight_fig = create_weight_distribution_chart(
        distribution.weights if distribution else [],
        unit=unit,
    )
    timeline_fig = create_stash_by_time_chart(
        rollups=report.periodic_monthly if report else None,
        unit=unit,
    )
    projects_fig = create_projects_pie_chart(
        project_usages or [],
        unit=unit,
    )
    flow_fig = create_monthly_flow_chart(
        report.periodic_monthly if report else [],
        unit=unit,
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
                                    style={"height": "380px", "width": "100%"},
                                ),
                                type="circle",
                                color="#8e6bb3",
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
                                    style={"height": "350px", "width": "100%"},
                                ),
                                type="circle",
                                color="#8e6bb3",
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
                                    style={"height": "350px", "width": "100%"},
                                ),
                                type="circle",
                                color="#8e6bb3",
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
                                "Projects Made from Stash",
                                className="m-0 text-light fs-6 fw-bold",
                            ),
                            className="bg-transparent border-secondary",
                        ),
                        dbc.CardBody(
                            dcc.Loading(
                                dcc.Graph(
                                    id="analytics-projects-chart",
                                    figure=projects_fig,
                                    config={"displayModeBar": False, "responsive": True},
                                    style={"height": "350px", "width": "100%"},
                                ),
                                type="circle",
                                color="#8e6bb3",
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
                                    style={"height": "350px", "width": "100%"},
                                ),
                                type="circle",
                                color="#8e6bb3",
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
                    html.H4("Stash Analytics", className="text-light fw-bold mb-1"),
                    html.P("Real-time inventory breakdowns, timeline trends, project utilization, and net flow history.", className="text-muted small mb-3"),
                ],
                className="mb-3",
            ),
            html.Div(kpi_cards, id="analytics-kpi-container"),
            unit_bar,
            charts_row_1,
            charts_row_2,
            charts_row_3,
        ],
        id="analytics-container",
        fluid=True,
        className="p-0",
    )
