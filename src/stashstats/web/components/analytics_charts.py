"""Plotly chart generation functions for Stash Analytics dashboard."""

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


def create_fiber_donut_chart(fibers: list[CategoryDistribution]) -> go.Figure:
    """Generate a donut pie chart representing fiber composition distributions.

    Args:
        fibers: List of CategoryDistribution objects for fiber categories.

    Returns:
        Configured Plotly Figure.
    """
    if not fibers or all(f.total_yards == 0 for f in fibers):
        return _create_empty_figure("No fiber distribution data available")

    labels = [f.name for f in fibers]
    values = [f.total_yards for f in fibers]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                textinfo="label+percent",
                marker={"colors": PALETTE[: len(labels)]},
                hovertemplate="<b>%{label}</b><br>Yardage: %{value:,.0f} yds<br>Share: %{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        **CHART_THEME,
        showlegend=True,
        legend={"orientation": "h", "yanchor": "bottom", "y": -0.2, "xanchor": "center", "x": 0.5},
    )
    return fig


def create_weight_distribution_chart(weights: list[CategoryDistribution]) -> go.Figure:
    """Generate a bar chart of stash breakdown by yarn weight classification.

    Args:
        weights: List of CategoryDistribution objects for yarn weights.

    Returns:
        Configured Plotly Figure.
    """
    if not weights or all(w.total_yards == 0 for w in weights):
        return _create_empty_figure("No yarn weight data available")

    x_labels = [w.name for w in weights]
    y_values = [w.total_yards for w in weights]
    skein_counts = [w.total_skeins for w in weights]

    fig = go.Figure(
        data=[
            go.Bar(
                x=x_labels,
                y=y_values,
                marker={"color": "#3498db", "line": {"color": "#2980b9", "width": 1}},
                customdata=skein_counts,
                hovertemplate="<b>%{x}</b><br>Yardage: %{y:,.0f} yds<br>Skeins: %{customdata:,.1f}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        **CHART_THEME,
        xaxis={"title": "Yarn Weight", "gridcolor": "#333"},
        yaxis={"title": "Total Yards", "gridcolor": "#333"},
    )
    return fig


def create_monthly_flow_chart(rollups: list[PeriodicRollup]) -> go.Figure:
    """Generate a dual-bar chart showing monthly stash acquisitions vs consumptions.

    Args:
        rollups: List of PeriodicRollup summaries.

    Returns:
        Configured Plotly Figure.
    """
    if not rollups:
        return _create_empty_figure("No historical flow data available")

    periods = [r.period for r in rollups]
    acquired = [r.acquired_yards for r in rollups]
    consumed = [r.consumed_yards for r in rollups]

    fig = go.Figure(
        data=[
            go.Bar(
                name="Acquired",
                x=periods,
                y=acquired,
                marker={"color": "#00bc8c"},
                hovertemplate="<b>%{x}</b><br>Acquired: %{y:,.0f} yds<extra></extra>",
            ),
            go.Bar(
                name="Consumed",
                x=periods,
                y=consumed,
                marker={"color": "#e74c3c"},
                hovertemplate="<b>%{x}</b><br>Consumed: %{y:,.0f} yds<extra></extra>",
            ),
        ]
    )

    fig.update_layout(
        **CHART_THEME,
        barmode="group",
        xaxis={"title": "Period", "gridcolor": "#333"},
        yaxis={"title": "Yards", "gridcolor": "#333"},
        legend={"orientation": "h", "yanchor": "bottom", "y": -0.2, "xanchor": "center", "x": 0.5},
    )
    return fig


def create_velocity_pace_chart(
    velocity_30d: RollingVelocity | None = None,
    velocity_90d: RollingVelocity | None = None,
    velocity_365d: RollingVelocity | None = None,
) -> go.Figure:
    """Generate a comparison chart of trailing consumption velocity horizons.

    Args:
        velocity_30d: Trailing 30-day pace.
        velocity_90d: Trailing 90-day pace.
        velocity_365d: Trailing 365-day pace.

    Returns:
        Configured Plotly Figure.
    """
    labels: list[str] = []
    daily_paces: list[float] = []
    monthly_paces: list[float] = []

    if velocity_30d:
        labels.append("30 Days")
        daily_paces.append(velocity_30d.yards_per_day)
        monthly_paces.append(velocity_30d.yards_per_month)
    if velocity_90d:
        labels.append("90 Days")
        daily_paces.append(velocity_90d.yards_per_day)
        monthly_paces.append(velocity_90d.yards_per_month)
    if velocity_365d:
        labels.append("365 Days")
        daily_paces.append(velocity_365d.yards_per_day)
        monthly_paces.append(velocity_365d.yards_per_month)

    if not labels:
        return _create_empty_figure("No velocity metrics available")

    fig = go.Figure(
        data=[
            go.Bar(
                x=labels,
                y=monthly_paces,
                marker={"color": "#9b59b6"},
                customdata=daily_paces,
                hovertemplate="<b>%{x} Horizon</b><br>Burn Rate: %{y:,.1f} yds/month<br>Daily: %{customdata:,.1f} yds/day<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        **CHART_THEME,
        xaxis={"title": "Trailing Horizon Window", "gridcolor": "#333"},
        yaxis={"title": "Estimated Yards / Month", "gridcolor": "#333"},
    )
    return fig
