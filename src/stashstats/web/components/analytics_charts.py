"""Plotly chart generation functions for Stash Analytics dashboard."""

from typing import Any
import plotly.graph_objects as go

from stashstats.analytics.distributions import CategoryDistribution
from stashstats.models.analytics import PeriodicRollup, ProjectUsageRecord, RollingVelocity

CHART_THEME = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#e0e0e0", "family": "Inter, Roboto, sans-serif"},
    "margin": {"l": 55, "r": 25, "t": 35, "b": 45},
    "autosize": True,
}

PALETTE = [
    "#8b5cf6",  # Violet Purple
    "#3b82f6",  # Royal Blue
    "#ec4899",  # Vivid Berry Pink
    "#06b6d4",  # Sky Cyan
    "#a855f7",  # Amethyst Purple
    "#d946ef",  # Orchid Magenta
    "#6366f1",  # Indigo Iris
    "#0ea5e9",  # Deep Sky Blue
    "#f43f5e",  # Rose Pink
    "#c084fc",  # Soft Lilac
    "#2563eb",  # Cobalt Blue
    "#db2777",  # Deep Rose
]


def _get_unit_meta(unit: str) -> tuple[str, str]:
    """Resolve display label and symbol for unit."""
    u = (unit or "yards").lower()
    if u in ("meters", "meter", "m"):
        return "Meters", "m"
    if u in ("grams", "gram", "g"):
        return "Grams", "g"
    if u in ("skeins", "skein", "sk"):
        return "Skeins", "sk"
    return "Yards", "yds"


def _create_empty_figure(message: str = "No data available") -> go.Figure:
    """Create an empty figure placeholder with centered message."""
    fig = go.Figure()
    fig.update_layout(
        **CHART_THEME,
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": message,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 14, "color": "#888"},
            }
        ],
    )
    return fig


def create_fiber_donut_chart(
    distributions: list[CategoryDistribution],
    unit: str = "yards",
) -> go.Figure:
    """Generate a donut pie chart of fiber content distribution.

    Args:
        distributions: List of CategoryDistribution objects for fibers.
        unit: Quantity dimension ('yards', 'meters', 'grams', 'skeins').

    Returns:
        Configured Plotly Figure.
    """
    label_unit, symbol = _get_unit_meta(unit)

    if not distributions:
        return _create_empty_figure("No fiber data available")

    labels = [d.name for d in distributions]
    if symbol == "m":
        values = [d.total_meters for d in distributions]
    elif symbol == "g":
        values = [d.total_grams for d in distributions]
    elif symbol == "sk":
        values = [d.total_skeins for d in distributions]
    else:
        values = [d.total_yards for d in distributions]

    if not values or all(v == 0 for v in values):
        return _create_empty_figure("No fiber quantities recorded")

    slice_colors = [PALETTE[i % len(PALETTE)] for i in range(len(labels))]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                textinfo="label+percent",
                marker={
                    "colors": slice_colors,
                    "line": {"color": "#1f2428", "width": 2},
                },
                hovertemplate=f"<b>%{{label}}</b><br>{label_unit}: %{{value:,.1f}} {symbol}<br>Share: %{{percent}}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        **CHART_THEME,
        showlegend=True,
        legend={"orientation": "h", "yanchor": "bottom", "y": -0.2, "xanchor": "center", "x": 0.5},
    )
    return fig


def create_weight_distribution_chart(
    distributions: list[CategoryDistribution],
    unit: str = "yards",
) -> go.Figure:
    """Generate a horizontal or vertical bar chart for yarn weight categories.

    Args:
        distributions: List of CategoryDistribution objects for yarn weights.
        unit: Quantity dimension ('yards', 'meters', 'grams', 'skeins').

    Returns:
        Configured Plotly Figure.
    """
    label_unit, symbol = _get_unit_meta(unit)

    if not distributions:
        return _create_empty_figure("No yarn weight data available")

    def extract_val(w: CategoryDistribution) -> float:
        if symbol == "m":
            return w.total_meters if w.total_meters > 0 else w.total_yards * 0.9144
        if symbol == "g":
            return w.total_grams
        if symbol == "sk":
            return w.total_skeins
        return w.total_yards

    if all(extract_val(w) == 0 for w in distributions):
        return _create_empty_figure("No weight quantities recorded")

    x_labels = [w.name for w in distributions]
    y_values = [extract_val(w) for w in distributions]
    item_counts = [w.count for w in distributions]
    bar_colors = [PALETTE[i % len(PALETTE)] for i in range(len(x_labels))]

    fig = go.Figure(
        data=[
            go.Bar(
                x=x_labels,
                y=y_values,
                marker={
                    "color": bar_colors,
                    "line": {"color": "rgba(255, 255, 255, 0.25)", "width": 1.5},
                },
                customdata=item_counts,
                hovertemplate=f"<b>%{{x}}</b><br>{label_unit}: %{{y:,.1f}} {symbol}<br>Items: %{{customdata}}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        **CHART_THEME,
        xaxis={"title": "Yarn Weight", "gridcolor": "#333"},
        yaxis={"title": f"Total {label_unit} ({symbol})", "gridcolor": "#333"},
    )
    return fig


def create_stash_by_time_chart(
    items: list[Any] | None = None,
    rollups: list[PeriodicRollup] | None = None,
    unit: str = "yards",
) -> go.Figure:
    """Generate a timeline area chart of stash volume over time.

    Args:
        items: Optional list of StashItem objects.
        rollups: Optional list of PeriodicRollup summaries.
        unit: Quantity dimension ('yards', 'meters', 'grams', 'skeins').

    Returns:
        Configured Plotly Figure.
    """
    label_unit, symbol = _get_unit_meta(unit)

    if rollups:
        sorted_rollups = sorted(rollups, key=lambda r: r.period)
        periods = [r.period for r in sorted_rollups]
        cum_values = []
        total = 0.0
        for r in sorted_rollups:
            if symbol == "sk":
                total += r.net_skeins
            elif symbol == "m":
                total += r.net_yards * 0.9144
            elif symbol == "g":
                total += r.net_yards * 0.45
            else:
                total += r.net_yards
            cum_values.append(max(0.0, total))

        if not periods or all(y == 0 for y in cum_values):
            return _create_empty_figure("No timeline data available")

        fig = go.Figure(
            data=[
                go.Scatter(
                    x=periods,
                    y=cum_values,
                    mode="lines+markers",
                    fill="tozeroy",
                    line={"color": "#0ea5e9", "width": 3, "shape": "spline"},
                    marker={"size": 7, "color": "#ec4899", "line": {"color": "#ffffff", "width": 1.5}},
                    fillcolor="rgba(14, 165, 233, 0.2)",
                    hovertemplate=f"<b>%{{x}}</b><br>Net Stash: %{{y:,.1f}} {symbol}<extra></extra>",
                )
            ]
        )
        fig.update_layout(
            **CHART_THEME,
            xaxis={"title": "Timeline", "gridcolor": "#333", "automargin": True},
            yaxis={"title": f"Total Stash ({symbol})", "gridcolor": "#333", "rangemode": "tozero", "automargin": True},
        )
        return fig

    if items:
        dated_items: list[tuple[str, float]] = []
        for item in items:
            date_val = (
                getattr(item, "purchased", None)
                or (item.primary_pack.purchased_date if getattr(item, "primary_pack", None) and item.primary_pack and item.primary_pack.purchased_date else None)
                or (item.packs[0].purchased_date if getattr(item, "packs", None) and item.packs and item.packs[0].purchased_date else None)
                or getattr(item, "created_at", None)
                or (item.first_photo.created_at[:10] if getattr(item, "first_photo", None) and getattr(item.first_photo, "created_at", None) else None)
                or "Undated"
            )

            if symbol == "m":
                qty = (
                    getattr(item, "meters_remaining", None)
                    if getattr(item, "meters_remaining", None) is not None
                    else getattr(item, "total_meters", None)
                )
                if qty is None:
                    yd = getattr(item, "yards_remaining", None) if getattr(item, "yards_remaining", None) is not None else getattr(item, "total_yards", 0.0)
                    qty = (yd or 0.0) * 0.9144
            elif symbol == "g":
                qty = (
                    getattr(item, "grams_remaining", None)
                    if getattr(item, "grams_remaining", None) is not None
                    else getattr(item, "total_grams", 0.0)
                )
            elif symbol == "sk":
                qty = (
                    getattr(item, "skeins_remaining", None)
                    if getattr(item, "skeins_remaining", None) is not None
                    else getattr(item, "skeins", 0.0)
                )
            else:
                qty = (
                    getattr(item, "yards_remaining", None)
                    if getattr(item, "yards_remaining", None) is not None
                    else getattr(item, "total_yards", 0.0)
                )

            period_key = str(date_val)[:7].replace("/", "-") if len(str(date_val)) >= 7 and date_val != "Undated" else "Undated"
            dated_items.append((period_key, qty or 0.0))

        period_totals: dict[str, float] = {}
        for period, val in dated_items:
            period_totals[period] = period_totals.get(period, 0.0) + val

        sorted_periods = sorted([p for p in period_totals.keys() if p != "Undated"])
        if not sorted_periods:
            if "Undated" in period_totals:
                sorted_periods = ["Active Stash"]
                cum_values = [period_totals["Undated"]]
            else:
                return _create_empty_figure("No stash timeline data available")
        else:
            cum_values = []
            running = 0.0
            for p in sorted_periods:
                running += period_totals[p]
                cum_values.append(running)

        fig = go.Figure(
            data=[
                go.Scatter(
                    x=sorted_periods,
                    y=cum_values,
                    mode="lines+markers",
                    fill="tozeroy",
                    line={"color": "#0ea5e9", "width": 3, "shape": "spline"},
                    marker={"size": 7, "color": "#ec4899", "line": {"color": "#ffffff", "width": 1.5}},
                    fillcolor="rgba(14, 165, 233, 0.2)",
                    hovertemplate=f"<b>%{{x}}</b><br>Cumulative Inflow: %{{y:,.1f}} {symbol}<extra></extra>",
                )
            ]
        )
        fig.update_layout(
            **CHART_THEME,
            xaxis={"title": "Timeline", "gridcolor": "#333", "automargin": True},
            yaxis={"title": f"Cumulative Inflow ({symbol})", "gridcolor": "#333", "rangemode": "tozero", "automargin": True},
        )
        return fig

    return _create_empty_figure("No stash timeline data available")


def create_monthly_flow_chart(
    rollups: list[PeriodicRollup],
    unit: str = "yards",
) -> go.Figure:
    """Generate a dual-bar chart showing monthly stash acquisitions vs consumptions.

    Args:
        rollups: List of PeriodicRollup summaries.
        unit: Quantity dimension ('yards', 'meters', 'grams', 'skeins').

    Returns:
        Configured Plotly Figure.
    """
    label_unit, symbol = _get_unit_meta(unit)

    if not rollups:
        return _create_empty_figure("No historical flow data available")

    periods = [r.period for r in rollups]
    if symbol == "sk":
        acquired = [r.acquired_skeins for r in rollups]
        consumed = [r.consumed_skeins for r in rollups]
    elif symbol == "m":
        acquired = [r.acquired_yards * 0.9144 for r in rollups]
        consumed = [r.consumed_yards * 0.9144 for r in rollups]
    elif symbol == "g":
        acquired = [r.acquired_yards * 0.45 for r in rollups]
        consumed = [r.consumed_yards * 0.45 for r in rollups]
    else:
        acquired = [r.acquired_yards for r in rollups]
        consumed = [r.consumed_yards for r in rollups]

    fig = go.Figure(
        data=[
            go.Bar(
                name="Acquired",
                x=periods,
                y=acquired,
                marker={"color": "#3b82f6", "line": {"color": "rgba(255, 255, 255, 0.2)", "width": 1}},
                hovertemplate=f"<b>%{{x}}</b><br>Acquired: %{{y:,.1f}} {symbol}<extra></extra>",
            ),
            go.Bar(
                name="Consumed",
                x=periods,
                y=consumed,
                marker={"color": "#ec4899", "line": {"color": "rgba(255, 255, 255, 0.2)", "width": 1}},
                hovertemplate=f"<b>%{{x}}</b><br>Consumed: %{{y:,.1f}} {symbol}<extra></extra>",
            ),
        ]
    )

    fig.update_layout(
        **CHART_THEME,
        barmode="group",
        xaxis={"title": "Period", "gridcolor": "#333"},
        yaxis={"title": f"{label_unit} ({symbol})", "gridcolor": "#333"},
        legend={"orientation": "h", "yanchor": "bottom", "y": -0.2, "xanchor": "center", "x": 0.5},
    )
    return fig


def create_velocity_pace_chart(
    velocity_30d: RollingVelocity | None = None,
    velocity_90d: RollingVelocity | None = None,
    velocity_365d: RollingVelocity | None = None,
    unit: str = "yards",
) -> go.Figure:
    """Generate a comparison chart of trailing consumption velocity horizons.

    Args:
        velocity_30d: Trailing 30-day pace.
        velocity_90d: Trailing 90-day pace.
        velocity_365d: Trailing 365-day pace.
        unit: Quantity dimension ('yards', 'meters', 'grams', 'skeins').

    Returns:
        Configured Plotly Figure.
    """
    label_unit, symbol = _get_unit_meta(unit)

    def extract_monthly_daily(v: RollingVelocity) -> tuple[float, float]:
        if symbol == "sk":
            return v.skeins_per_month, v.skeins_per_month / 30.4375
        if symbol == "m":
            return v.yards_per_month * 0.9144, v.yards_per_day * 0.9144
        if symbol == "g":
            return v.yards_per_month * 0.45, v.yards_per_day * 0.45
        return v.yards_per_month, v.yards_per_day

    labels: list[str] = []
    daily_paces: list[float] = []
    monthly_paces: list[float] = []

    if velocity_30d:
        m, d = extract_monthly_daily(velocity_30d)
        labels.append("30 Days")
        daily_paces.append(d)
        monthly_paces.append(m)
    if velocity_90d:
        m, d = extract_monthly_daily(velocity_90d)
        labels.append("90 Days")
        daily_paces.append(d)
        monthly_paces.append(m)
    if velocity_365d:
        m, d = extract_monthly_daily(velocity_365d)
        labels.append("365 Days")
        daily_paces.append(d)
        monthly_paces.append(m)

    if not labels:
        return _create_empty_figure("No velocity metrics available")

    fig = go.Figure(
        data=[
            go.Bar(
                x=labels,
                y=monthly_paces,
                marker={"color": "#9b59b6"},
                customdata=daily_paces,
                hovertemplate=f"<b>%{{x}} Horizon</b><br>Burn Rate: %{{y:,.1f}} {symbol}/mo<br>Daily: %{{customdata:,.1f}} {symbol}/day<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        **CHART_THEME,
        xaxis={"title": "Trailing Horizon Window", "gridcolor": "#333"},
        yaxis={"title": f"Estimated {label_unit} / Month", "gridcolor": "#333"},
    )
    return fig


def create_projects_pie_chart(
    usages: list[ProjectUsageRecord],
    unit: str = "yards",
) -> go.Figure:
    """Generate a donut pie chart of stash yarn consumption by project.

    Args:
        usages: List of ProjectUsageRecord correlation objects.
        unit: Quantity dimension ('yards', 'meters', 'grams', 'skeins').

    Returns:
        Configured Plotly Figure.
    """
    label_unit, symbol = _get_unit_meta(unit)

    if not usages:
        return _create_empty_figure("No projects linked to stash yarn")

    project_totals: dict[str, float] = {}
    for u in usages:
        p_name = u.project_name or f"Project #{u.project_id}"
        if symbol == "m":
            val = u.meters_used
        elif symbol == "g":
            val = u.grams_used
        elif symbol == "sk":
            val = u.skeins_used
        else:
            val = u.yards_used
        if val > 0:
            project_totals[p_name] = project_totals.get(p_name, 0.0) + val

    labels = list(project_totals.keys())
    values = [project_totals[l] for l in labels]

    if not values or all(v == 0 for v in values):
        return _create_empty_figure("No project yarn consumption recorded")

    slice_colors = [PALETTE[i % len(PALETTE)] for i in range(len(labels))]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                textinfo="label+percent",
                marker={
                    "colors": slice_colors,
                    "line": {"color": "#1f2428", "width": 2},
                },
                hovertemplate=f"<b>%{{label}}</b><br>{label_unit}: %{{value:,.1f}} {symbol}<br>Share: %{{percent}}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        **CHART_THEME,
        showlegend=True,
        legend={"orientation": "h", "yanchor": "bottom", "y": -0.2, "xanchor": "center", "x": 0.5},
    )
    return fig

