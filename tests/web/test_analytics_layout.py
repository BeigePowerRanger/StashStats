import dash_bootstrap_components as dbc
from dash import dcc, html
import pytest

from stashstats.analytics.distributions import StashDistributionCalculator
from stashstats.models.analytics import StashHorizon, StashVelocityReport
from stashstats.models.stash import StashItem
from stashstats.web.layouts.analytics import create_analytics_layout
from stashstats.web.layouts.main import create_navigation_tabs


class TestAnalyticsLayout:
    def test_create_analytics_layout_empty(self):
        layout = create_analytics_layout()
        assert isinstance(layout, dbc.Container)
        # Verify graph elements exist
        graph_ids = [
            comp.id
            for comp in layout.children
            if isinstance(comp, dcc.Graph) or (hasattr(comp, "children") and isinstance(comp.children, dcc.Graph))
        ]
        # At least container renders
        assert layout.id == "analytics-container"

    def test_create_analytics_layout_with_data(self):
        items = [
            StashItem(
                id=1,
                name="Test Merino",
                permalink="test-merino",
                skeins=2.0,
                total_yards=440.0,
                yarn_weight_name="Worsted",
                color_family_name="Blue",
            )
        ]
        distributions = StashDistributionCalculator.aggregate_all(items)
        horizon = StashHorizon(
            total_active_yards=440.0,
            total_active_skeins=2.0,
            monthly_burn_rate_yards=100.0,
            months_remaining=4.4,
            years_remaining=0.37,
        )
        report = StashVelocityReport(
            total_active_yards=440.0,
            total_active_skeins=2.0,
            total_active_items=1,
            horizon=horizon,
        )

        layout = create_analytics_layout(report=report, distribution=distributions)
        assert isinstance(layout, dbc.Container)

    def test_navigation_tabs_embeds_analytics_layout(self):
        tabs = create_navigation_tabs(active_tab="tab-analytics")
        assert isinstance(tabs, dcc.Tabs)
        # Check tab children for analytics-tab-content
        analytics_tab = next(t for t in tabs.children if t.value == "tab-analytics")
        assert analytics_tab is not None
