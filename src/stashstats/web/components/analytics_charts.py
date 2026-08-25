"""Plotly chart generation functions for Stash Analytics dashboard."""

from typing import Any
import plotly.graph_objects as go

from stashstats.analytics.distributions import CategoryDistribution
from stashstats.models.analytics import PeriodicRollup, RollingVelocity

CHART_THEME = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#e0e0e0", "family": "Inter, Roboto, sans-serif"},
    "margin": {"l": 30, "r": 20, "t": 40, "b": 30},
}

PALETTE = [
    "#00bc8c",
    "#3498db",
    "#9b59b6",
    "#f39c12",
    "#e74c3c",
    "#1abc9c",
    "#e67e22",
    "#fd7e14",
    "#6f42c1",
    "#20c997",
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
    fibers: list[CategoryDistribution],
    unit: str = "yards",
) -> go.Figure:
    """Generate a donut pie chart representing fiber composition distributions.

    Args:
        fibers: List of CategoryDistribution objects for fiber categories.
        unit: Quantity dimension ('yards', 'meters', 'grams', 'skeins').

    Returns:
        Configured Plotly Figure.
    """
    label_unit, symbol = _get_unit_meta(unit)

    def extract_val(f: CategoryDistribution) -> float:
        if symbol == "m":
            return f.total_meters if f.total_meters > 0 else f.total_yards * 0.9144
        if symbol == "g":
            return f.total_grams
        if symbol == "sk":
            return f.total_skeins
        return f.total_yards

    if not fibers or all(extract_val(f) == 0 for f in fibers):
        return _create_empty_figure(f"No fiber {label_unit.lower()} distribution data available")

    labels = [f.name for f in fibers]
    values = [extract_val(f) for f in fibers]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                textinfo="label+percent",
                marker={"colors": PALETTE[: len(labels)]},
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
    weights: list[CategoryDistribution],
    unit: str = "yards",
) -> go.Figure:
    """Generate a bar chart of stash breakdown by yarn weight classification.

    Args:
        weights: List of CategoryDistribution objects for yarn weights.
        unit: Quantity dimension ('yards', 'meters', 'grams', 'skeins').

    Returns:
        Configured Plotly Figure.
    """
    label_unit, symbol = _get_unit_meta(unit)

    def extract_val(w: CategoryDistribution) -> float:
        if symbol == "m":
            return w.total_meters if w.total_meters > 0 else w.total_yards * 0.9144
        if symbol == "g":
            return w.total_grams
        if symbol == "sk":
            return w.total_skeins
        return w.total_yards

    if not weights or all(extract_val(w) == 0 for w in weights):
        return _create_empty_figure(f"No yarn weight {label_unit.lower()} data available")

    x_labels = [w.name for w in weights]
    y_values = [extract_val(w) for w in weights]
    item_counts = [w.count for w in weights]

    fig = go.Figure(
        data=[
            go.Bar(
                x=x_labels,
                y=y_values,
                marker={"color": "#3498db", "line": {"color": "#2980b9", "width": 1}},
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
                    line={"color": "#00bc8c", "width": 3, "shape": "spline"},
                    marker={"size": 6, "color": "#00bc8c"},
                    fillcolor="rgba(0, 188, 140, 0.15)",
                    hovertemplate=f"<b>%{{x}}</b><br>Net Stash: %{{y:,.1f}} {symbol}<extra></extra>",
                )
            ]
        )
        fig.update_layout(
            **CHART_THEME,
            xaxis={"title": "Timeline", "gridcolor": "#333"},
            yaxis={"title": f"Total Stash ({symbol})", "gridcolor": "#333"},
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
                    line={"color": "#00bc8c", "width": 3, "shape": "spline"},
                    marker={"size": 6, "color": "#00bc8c"},
                    fillcolor="rgba(0, 188, 140, 0.15)",
                    hovertemplate=f"<b>%{{x}}</b><br>Cumulative Inflow: %{{y:,.1f}} {symbol}<extra></extra>",
                )
            ]
        )
        fig.update_layout(
            **CHART_THEME,
            xaxis={"title": "Timeline", "gridcolor": "#333"},
            yaxis={"title": f"Cumulative Inflow ({symbol})", "gridcolor": "#333"},
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
                marker={"color": "#00bc8c"},
                hovertemplate=f"<b>%{{x}}</b><br>Acquired: %{{y:,.1f}} {symbol}<extra></extra>",
            ),
            go.Bar(
                name="Consumed",
                x=periods,
                y=consumed,
                marker={"color": "#e74c3c"},
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
