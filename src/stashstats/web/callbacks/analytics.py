"""Reactive Dash callbacks for Stash Analytics filtering, chart rendering, and metric updates."""

import logging
from typing import Any

import dash
import plotly.graph_objects as go
from dash import Input, Output, State, callback_context

from stashstats.analytics.distributions import StashDistributionCalculator
from stashstats.analytics.velocity import StashVelocityCalculator
from stashstats.models.analytics import StashHorizon, StashVelocityReport
from stashstats.models.stash import StashItem
from stashstats.web.components.analytics import create_kpi_summary_cards
from stashstats.web.components.analytics_charts import (
    create_fiber_donut_chart,
    create_monthly_flow_chart,
    create_stash_by_time_chart,
    create_velocity_pace_chart,
    create_weight_distribution_chart,
)

logger = logging.getLogger("stashstats.web.analytics")


def _filter_stash_item(
    item: StashItem,
    selected_weights: list[str] | None = None,
    selected_colors: list[str] | None = None,
    search_query: str | None = None,
    min_grams: float | None = None,
    max_grams: float | None = None,
    min_yards: float | None = None,
    max_yards: float | None = None,
    min_meters: float | None = None,
    max_meters: float | None = None,
    min_skeins: float | None = None,
    max_skeins: float | None = None,
) -> bool:
    """Check if a StashItem satisfies current filter criteria."""
    # 1. Weight filter
    if selected_weights:
        weight_name = (
            item.yarn_weight_name
            or (item.yarn.yarn_weight.name if item.yarn and item.yarn.yarn_weight else None)
            or (item.personal_yarn_weight.name if item.personal_yarn_weight else None)
            or "Uncategorized"
        )
        if weight_name not in selected_weights:
            return False

    # 2. Color filter
    if selected_colors:
        color_name = item.color_family_name or "Uncategorized"
        if color_name not in selected_colors:
            return False

    # 3. Search query filter
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        searchable_text = " ".join(
            filter(
                None,
                [
                    item.name,
                    item.yarn.name if item.yarn else None,
                    item.yarn.yarn_company_name if item.yarn else None,
                    item.colorway_name,
                    item.yarn_weight_name,
                    item.color_family_name,
                ],
            )
        ).lower()
        if q not in searchable_text:
            return False

    # 4. Quantity filters (Grams, Yards, Meters, Skeins)
    grams = (
        item.total_grams
        if item.total_grams is not None
        else getattr(item, "grams", None)
    )
    if grams is None and item.primary_pack and item.primary_pack.total_grams is not None:
        grams = item.primary_pack.total_grams

    yards = (
        getattr(item, "yards_remaining", None)
        if getattr(item, "yards_remaining", None) is not None
        else item.total_yards
    )
    if yards is None and getattr(item, "yards", None) is not None:
        yards = getattr(item, "yards", None)
    if yards is None and item.primary_pack and item.primary_pack.total_yards is not None:
        yards = item.primary_pack.total_yards

    meters = (
        getattr(item, "meters_remaining", None)
        if getattr(item, "meters_remaining", None) is not None
        else item.total_meters
    )
    if meters is None and getattr(item, "meters", None) is not None:
        meters = getattr(item, "meters", None)
    if meters is None and item.primary_pack and item.primary_pack.total_meters is not None:
        meters = item.primary_pack.total_meters
    if meters is None and yards is not None:
        meters = yards * 0.9144

    skeins = (
        getattr(item, "skeins_remaining", None)
        if getattr(item, "skeins_remaining", None) is not None
        else item.skeins
    )
    if skeins is None and item.primary_pack and item.primary_pack.skeins is not None:
        skeins = item.primary_pack.skeins

    # Check Grams range
    if min_grams is not None and (grams is None or grams < min_grams):
        return False
    if max_grams is not None and (grams is None or grams > max_grams):
        return False

    # Check Yards range
    if min_yards is not None and (yards is None or yards < min_yards):
        return False
    if max_yards is not None and (yards is None or yards > max_yards):
        return False

    # Check Meters range
    if min_meters is not None and (meters is None or meters < min_meters):
        return False
    if max_meters is not None and (meters is None or meters > max_meters):
        return False

    # Check Skeins range
    if min_skeins is not None and (skeins is None or skeins < min_skeins):
        return False
    if max_skeins is not None and (skeins is None or skeins > max_skeins):
        return False

    return True


def update_analytics_dashboard_logic(
    raw_stash_data: list[dict[str, Any]] | None,
    selected_weights: list[str] | None = None,
    selected_colors: list[str] | None = None,
    search_query: str | None = None,
    min_grams: float | None = None,
    max_grams: float | None = None,
    min_yards: float | None = None,
    max_yards: float | None = None,
    min_meters: float | None = None,
    max_meters: float | None = None,
    min_skeins: float | None = None,
    max_skeins: float | None = None,
    reset_clicks: int | None = None,
    triggered_id: str | None = None,
) -> tuple[Any, ...]:
    """Pure calculation logic for updating the analytics dashboard components and charts.

    Returns:
        tuple containing (kpi_cards, fiber_fig, weight_fig, timeline_fig, flow_fig, velocity_fig,
        weight_val, color_val, search_val, min_g, max_g, min_y, max_y, min_m, max_m, min_sk, max_sk).
    """
    if triggered_id == "analytics-filter-reset":
        selected_weights = None
        selected_colors = None
        search_query = None
        min_grams = None
        max_grams = None
        min_yards = None
        max_yards = None
        min_meters = None
        max_meters = None
        min_skeins = None
        max_skeins = None

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

    filtered_items = [
        item
        for item in stash_items
        if _filter_stash_item(
            item,
            selected_weights=selected_weights,
            selected_colors=selected_colors,
            search_query=search_query,
            min_grams=min_grams,
            max_grams=max_grams,
            min_yards=min_yards,
            max_yards=max_yards,
            min_meters=min_meters,
            max_meters=max_meters,
            min_skeins=min_skeins,
            max_skeins=max_skeins,
        )
    ]

    # Calculate distributions
    distributions = StashDistributionCalculator.aggregate_all(filtered_items)

    # Compute baseline metrics from filtered items
    total_yards = sum(
        (getattr(item, "yards_remaining", None) if getattr(item, "yards_remaining", None) is not None else item.total_yards)
        or 0.0
        for item in filtered_items
    )
    total_skeins = sum(
        (getattr(item, "skeins_remaining", None) if getattr(item, "skeins_remaining", None) is not None else item.skeins)
        or 0.0
        for item in filtered_items
    )
    total_items = len(filtered_items)

    # Velocity Report calculation
    histories: dict[int, Any] = {}
    report = StashVelocityCalculator.generate_report(filtered_items, histories)

    monthly_burn_rate = (
        report.horizon.monthly_burn_rate_yards if report.horizon else 0.0
    )
    months_remaining = (
        report.horizon.months_remaining if report.horizon else None
    )

    kpi_cards = create_kpi_summary_cards(
        total_yards=total_yards,
        total_skeins=total_skeins,
        total_items=total_items,
        monthly_burn_rate=monthly_burn_rate,
        months_remaining=months_remaining,
    )

    fiber_fig = create_fiber_donut_chart(distributions.fibers)
    weight_fig = create_weight_distribution_chart(distributions.weights)
    timeline_fig = create_stash_by_time_chart(
        items=filtered_items,
        rollups=report.periodic_monthly if report else None,
    )
    flow_fig = create_monthly_flow_chart(report.periodic_monthly)
    velocity_fig = create_velocity_pace_chart(
        velocity_30d=report.velocity_30d,
        velocity_90d=report.velocity_90d,
        velocity_365d=report.velocity_365d,
    )

    return (
        kpi_cards,
        fiber_fig,
        weight_fig,
        timeline_fig,
        flow_fig,
        velocity_fig,
        selected_weights,
        selected_colors,
        search_query,
        min_grams,
        max_grams,
        min_yards,
        max_yards,
        min_meters,
        max_meters,
        min_skeins,
        max_skeins,
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
        Output("analytics-filter-weight", "value"),
        Output("analytics-filter-color", "value"),
        Output("analytics-filter-search", "value"),
        Output("analytics-filter-min-grams", "value"),
        Output("analytics-filter-max-grams", "value"),
        Output("analytics-filter-min-yards", "value"),
        Output("analytics-filter-max-yards", "value"),
        Output("analytics-filter-min-meters", "value"),
        Output("analytics-filter-max-meters", "value"),
        Output("analytics-filter-min-skeins", "value"),
        Output("analytics-filter-max-skeins", "value"),
        Input("stash-raw-store", "data"),
        Input("analytics-filter-weight", "value"),
        Input("analytics-filter-color", "value"),
        Input("analytics-filter-search", "value"),
        Input("analytics-filter-min-grams", "value"),
        Input("analytics-filter-max-grams", "value"),
        Input("analytics-filter-min-yards", "value"),
        Input("analytics-filter-max-yards", "value"),
        Input("analytics-filter-min-meters", "value"),
        Input("analytics-filter-max-meters", "value"),
        Input("analytics-filter-min-skeins", "value"),
        Input("analytics-filter-max-skeins", "value"),
        Input("analytics-filter-reset", "n_clicks"),
        prevent_initial_call=False,
    )
    def update_analytics_dashboard(
        raw_stash_data: list[dict[str, Any]] | None,
        selected_weights: list[str] | None,
        selected_colors: list[str] | None,
        search_query: str | None,
        min_grams: float | None,
        max_grams: float | None,
        min_yards: float | None,
        max_yards: float | None,
        min_meters: float | None,
        max_meters: float | None,
        min_skeins: float | None,
        max_skeins: float | None,
        reset_clicks: int | None,
    ):
        ctx = callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

        return update_analytics_dashboard_logic(
            raw_stash_data=raw_stash_data,
            selected_weights=selected_weights,
            selected_colors=selected_colors,
            search_query=search_query,
            min_grams=min_grams,
            max_grams=max_grams,
            min_yards=min_yards,
            max_yards=max_yards,
            min_meters=min_meters,
            max_meters=max_meters,
            min_skeins=min_skeins,
            max_skeins=max_skeins,
            reset_clicks=reset_clicks,
            triggered_id=triggered_id,
        )
