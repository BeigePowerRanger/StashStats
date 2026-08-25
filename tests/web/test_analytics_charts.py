import plotly.graph_objects as go
import pytest

from stashstats.analytics.distributions import CategoryDistribution
from stashstats.models.analytics import PeriodicRollup, RollingVelocity
from stashstats.models.stash import StashItem
from stashstats.web.components.analytics_charts import (
    create_fiber_donut_chart,
    create_monthly_flow_chart,
    create_stash_by_time_chart,
    create_velocity_pace_chart,
    create_weight_distribution_chart,
)


class TestAnalyticsCharts:
    def test_create_fiber_donut_chart(self):
        fibers = [
            CategoryDistribution(name="Merino", total_yards=1200.0, count=3, percentage_yards=60.0),
            CategoryDistribution(name="Silk", total_yards=800.0, count=2, percentage_yards=40.0),
        ]
        fig = create_fiber_donut_chart(fibers)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == "pie"
        assert list(fig.data[0].labels) == ["Merino", "Silk"]
        assert list(fig.data[0].values) == [1200.0, 800.0]

    def test_create_fiber_donut_chart_empty(self):
        fig = create_fiber_donut_chart([])
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.annotations) >= 1

    def test_create_weight_distribution_chart(self):
        weights = [
            CategoryDistribution(name="Worsted", total_yards=1500.0, count=4, total_skeins=6.0),
            CategoryDistribution(name="Fingering", total_yards=1000.0, count=2, total_skeins=3.0),
        ]
        fig = create_weight_distribution_chart(weights)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == "bar"
        assert list(fig.data[0].x) == ["Worsted", "Fingering"]
        assert list(fig.data[0].y) == [1500.0, 1000.0]

    def test_create_weight_distribution_chart_empty(self):
        fig = create_weight_distribution_chart([])
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.annotations) >= 1

    def test_create_monthly_flow_chart(self):
        rollups = [
            PeriodicRollup(period="2026-06", acquired_yards=500.0, consumed_yards=200.0, net_yards=300.0),
            PeriodicRollup(period="2026-07", acquired_yards=0.0, consumed_yards=400.0, net_yards=-400.0),
            PeriodicRollup(period="2026-08", acquired_yards=800.0, consumed_yards=300.0, net_yards=500.0),
        ]
        fig = create_monthly_flow_chart(rollups)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 2  # Acquired and Consumed bars
        assert list(fig.data[0].x) == ["2026-06", "2026-07", "2026-08"]

    def test_create_monthly_flow_chart_empty(self):
        fig = create_monthly_flow_chart([])
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.annotations) >= 1

    def test_create_velocity_pace_chart(self):
        v30 = RollingVelocity(window_days=30, yards_consumed=300.0, skeins_consumed=1.5, yards_per_day=10.0, yards_per_month=304.38, skeins_per_month=1.52)
        v90 = RollingVelocity(window_days=90, yards_consumed=720.0, skeins_consumed=3.6, yards_per_day=8.0, yards_per_month=243.5, skeins_per_month=1.22)
        v365 = RollingVelocity(window_days=365, yards_consumed=2190.0, skeins_consumed=10.0, yards_per_day=6.0, yards_per_month=182.6, skeins_per_month=0.83)

        fig = create_velocity_pace_chart(v30, v90, v365)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 1
        assert list(fig.data[0].x) == ["30 Days", "90 Days", "365 Days"]
        assert list(fig.data[0].y) == [304.38, 243.5, 182.6]

    def test_create_stash_by_time_chart_with_rollups(self):
        rollups = [
            PeriodicRollup(period="2026-01", acquired_yards=1000.0, consumed_yards=200.0, net_yards=800.0),
            PeriodicRollup(period="2026-02", acquired_yards=500.0, consumed_yards=300.0, net_yards=200.0),
            PeriodicRollup(period="2026-03", acquired_yards=200.0, consumed_yards=400.0, net_yards=-200.0),
        ]
        fig = create_stash_by_time_chart(rollups=rollups)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == "scatter"
        assert list(fig.data[0].x) == ["2026-01", "2026-02", "2026-03"]
        assert list(fig.data[0].y) == [800.0, 1000.0, 800.0]

    def test_create_stash_by_time_chart_with_items(self):
        items = [
            StashItem(id=1, name="Yarn A", permalink="yarn-a", created_at="2026-01-15T12:00:00Z", total_yards=400.0),
            StashItem(id=2, name="Yarn B", permalink="yarn-b", created_at="2026-02-10T12:00:00Z", total_yards=600.0),
        ]
        fig = create_stash_by_time_chart(items=items)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == "scatter"
        assert len(fig.data[0].x) >= 2

    def test_create_stash_by_time_chart_empty(self):
        fig = create_stash_by_time_chart()
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.annotations) >= 1
