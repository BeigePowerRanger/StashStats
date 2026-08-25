"""Reactive Dash callbacks for Stash Analytics chart rendering, metric updates, and unit switching."""

import logging
from typing import Any

import dash
import plotly.graph_objects as go
from dash import Input, Output, State, callback_context

from stashstats.analytics.distributions import StashDistributionCalculator
from stashstats.analytics.projects import StashProjectUsageCalculator
from stashstats.analytics.velocity import StashVelocityCalculator
from stashstats.models.analytics import StashHorizon, StashVelocityReport
from stashstats.models.project import Project
from stashstats.models.stash import StashItem
from stashstats.web.components.analytics import create_kpi_summary_cards
from stashstats.web.components.analytics_charts import (
    create_fiber_donut_chart,
    create_monthly_flow_chart,
    create_projects_pie_chart,
    create_stash_by_time_chart,
    create_velocity_pace_chart,
    create_weight_distribution_chart,
)

logger = logging.getLogger("stashstats.web.analytics")


def update_analytics_dashboard_logic(
    raw_stash_data: list[dict[str, Any]] | None,
    raw_projects_data: list[dict[str, Any]] | None = None,
    histories_data: dict[int, Any] | list[Any] | None = None,
    unit: str = "yards",
) -> tuple[Any, ...]:
    """Pure calculation logic for updating the analytics dashboard components and charts.

    Returns:
        tuple containing (kpi_cards, fiber_fig, weight_fig, timeline_fig, flow_fig, velocity_fig, projects_fig).
    """
    raw_items = raw_stash_data or []
    stash_items: list[StashItem] = []
    for d in raw_items:
        if isinstance(d, StashItem):
            stash_items.append(d)
        elif isinstance(d, dict):
            try:
                stash_items.append(StashItem.model_validate(d))
            except Exception:
                pass

    raw_projs = raw_projects_data or []
    project_items: list[Project] = []
    for p in raw_projs:
        if isinstance(p, Project):
            project_items.append(p)
        elif isinstance(p, dict):
            try:
                project_items.append(Project.model_validate(p))
            except Exception:
                pass

    # Extract histories embedded on stash items or raw_items if histories_data is None
    histories: dict[int, Any] = {}
    if isinstance(histories_data, dict):
        histories.update(histories_data)
    elif isinstance(histories_data, list):
        for idx, h in enumerate(histories_data):
            sid = h.get("stash_id") if isinstance(h, dict) else getattr(h, "stash_id", idx)
            histories.setdefault(sid or idx, []).append(h)
    else:
        for it in raw_items:
            if isinstance(it, dict):
                sid = it.get("id")
                if sid and it.get("history"):
                    histories[sid] = it["history"]
                elif sid and it.get("usage_history"):
                    histories[sid] = it["usage_history"]

    # Calculate distributions
    distributions = StashDistributionCalculator.aggregate_all(stash_items)

    # Correlate projects and stash usage
    project_usages = StashProjectUsageCalculator.correlate_projects_and_stash(
        stash_items=stash_items,
        projects=project_items,
        histories=histories,
    )

    # Compute baseline metrics
    total_yards = sum(
        (getattr(item, "yards_remaining", None) if getattr(item, "yards_remaining", None) is not None else item.total_yards)
        or 0.0
        for item in stash_items
    )
    total_meters = sum(
        (getattr(item, "meters_remaining", None) if getattr(item, "meters_remaining", None) is not None else item.total_meters)
        or ((getattr(item, "total_yards", 0.0) or 0.0) * 0.9144)
        for item in stash_items
    )
    total_grams = sum(
        (getattr(item, "grams_remaining", None) if getattr(item, "grams_remaining", None) is not None else item.total_grams)
        or 0.0
        for item in stash_items
    )
    total_skeins = sum(
        (getattr(item, "skeins_remaining", None) if getattr(item, "skeins_remaining", None) is not None else item.skeins)
        or 0.0
        for item in stash_items
    )
    total_items = len(stash_items)

    # Velocity Report calculation
    report = StashVelocityCalculator.generate_report(stash_items, histories)

    monthly_burn_rate = (
        report.horizon.monthly_burn_rate_yards if report.horizon else 0.0
    )
    months_remaining = (
        report.horizon.months_remaining if report.horizon else None
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

    fiber_fig = create_fiber_donut_chart(distributions.fibers, unit=unit)
    weight_fig = create_weight_distribution_chart(distributions.weights, unit=unit)
    timeline_fig = create_stash_by_time_chart(
        items=stash_items,
        rollups=report.periodic_monthly if report else None,
        unit=unit,
    )
    projects_fig = create_projects_pie_chart(project_usages, unit=unit)
    flow_fig = create_monthly_flow_chart(report.periodic_monthly, unit=unit)
    velocity_fig = create_velocity_pace_chart(
        velocity_30d=report.velocity_30d,
        velocity_90d=report.velocity_90d,
        velocity_365d=report.velocity_365d,
        unit=unit,
    )

    return (
        kpi_cards,
        fiber_fig,
        weight_fig,
        timeline_fig,
        flow_fig,
        velocity_fig,
        projects_fig,
    )


def register_analytics_callbacks(app: dash.Dash) -> None:
    """Register reactive event handlers and callbacks for the Stash Analytics dashboard."""

    @app.callback(
        Output("analytics-kpi-container", "children"),
        Output("analytics-fiber-chart", "figure"),
        Output("analytics-weight-chart", "figure"),
        Output("analytics-timeline-chart", "figure"),
        Output("analytics-flow-chart", "figure"),
        Output("analytics-velocity-chart", "figure"),
        Output("analytics-projects-chart", "figure"),
        Input("stash-raw-store", "data"),
        Input("analytics-unit-selector", "value"),
        State("modal-store-history", "data"),
        prevent_initial_call=False,
    )
    def update_analytics_dashboard(
        raw_stash_data: list[dict[str, Any]] | None,
        unit: str | None,
        modal_history: list[dict[str, Any]] | None = None,
    ):
        histories_data = modal_history if modal_history else None
        return update_analytics_dashboard_logic(
            raw_stash_data=raw_stash_data,
            raw_projects_data=None,
            histories_data=histories_data,
            unit=unit or "yards",
        )
