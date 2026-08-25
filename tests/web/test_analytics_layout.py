import dash_bootstrap_components as dbc
from dash import dcc, html
import pytest

from stashstats.analytics.distributions import StashDistributionCalculator
from stashstats.models.analytics import StashHorizon, StashVelocityReport
from stashstats.models.stash import StashItem
from stashstats.web.layouts.analytics import create_analytics_layout
from stashstats.web.layouts.main import create_navigation_tabs


def _find_component_by_id(component, target_id):
    """Recursively search for a component with matching id."""
    if getattr(component, "id", None) == target_id:
        return component
    children = getattr(component, "children", None)
    if isinstance(children, list):
        for child in children:
            res = _find_component_by_id(child, target_id)
            if res is not None:
                return res
    elif children is not None:
        return _find_component_by_id(children, target_id)
    return None


class TestAnalyticsLayout:
    def test_create_analytics_layout_empty(self):
        layout = create_analytics_layout()
        assert isinstance(layout, dbc.Container)
        assert layout.id == "analytics-container"
        assert _find_component_by_id(layout, "analytics-timeline-chart") is not None
        assert _find_component_by_id(layout, "analytics-projects-chart") is not None

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
        assert _find_component_by_id(layout, "analytics-projects-chart") is not None

    def test_navigation_tabs_embeds_analytics_layout(self):
        tabs = create_navigation_tabs(active_tab="tab-analytics")
        assert isinstance(tabs, dcc.Tabs)
        analytics_tab = next(t for t in tabs.children if t.value == "tab-analytics")
        assert analytics_tab is not None
