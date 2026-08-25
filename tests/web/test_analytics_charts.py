import plotly.graph_objects as go
import pytest

from stashstats.analytics.distributions import CategoryDistribution
from stashstats.models.analytics import PeriodicRollup, ProjectUsageRecord, RollingVelocity
from stashstats.web.components.analytics_charts import (
    create_fiber_donut_chart,
    create_monthly_flow_chart,
    create_projects_pie_chart,
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

    def test_create_stash_by_time_chart(self):
        rollups = [
            PeriodicRollup(period="2026-01", net_yards=300.0),
            PeriodicRollup(period="2026-02", net_yards=200.0),
        ]
        fig = create_stash_by_time_chart(rollups=rollups)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert list(fig.data[0].x) == ["2026-01", "2026-02"]
        assert list(fig.data[0].y) == [300.0, 500.0]

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

    def test_create_projects_pie_chart(self):
        records = [
            ProjectUsageRecord(
                project_id=1,
                project_name="Beanie Hat",
                pattern_name="Classic Ribbed Hat",
                yards_used=300.0,
                meters_used=274.0,
                grams_used=100.0,
                skeins_used=1.0,
            ),
            ProjectUsageRecord(
                project_id=2,
                project_name="Winter Scarf",
                pattern_name="Garter Scarf",
                yards_used=600.0,
                meters_used=548.0,
                grams_used=200.0,
                skeins_used=2.0,
            ),
        ]

        fig_yards = create_projects_pie_chart(records, unit="yards")
        assert isinstance(fig_yards, go.Figure)
        assert len(fig_yards.data) == 1
        assert fig_yards.data[0].type == "pie"
        assert list(fig_yards.data[0].labels) == ["Beanie Hat", "Winter Scarf"]
        assert list(fig_yards.data[0].values) == [300.0, 600.0]

        fig_grams = create_projects_pie_chart(records, unit="grams")
        assert list(fig_grams.data[0].values) == [100.0, 200.0]

        fig_meters = create_projects_pie_chart(records, unit="meters")
        assert list(fig_meters.data[0].values) == [274.0, 548.0]

        fig_skeins = create_projects_pie_chart(records, unit="skeins")
        assert list(fig_skeins.data[0].values) == [1.0, 2.0]

    def test_create_projects_pie_chart_empty(self):
        fig = create_projects_pie_chart([])
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.annotations) >= 1
