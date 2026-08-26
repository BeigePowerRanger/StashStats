import dash_bootstrap_components as dbc
from dash import html
import pytest

from stashstats.web.components.analytics import (
    create_kpi_summary_cards,
    create_unit_selector_bar,
)


class TestAnalyticsComponents:
    def test_create_kpi_summary_cards(self):
        row = create_kpi_summary_cards(
            total_yards=3500.0,
            total_skeins=15.0,
            total_items=8,
            monthly_burn_rate=500.0,
            months_remaining=7.0,
        )
        assert isinstance(row, dbc.Row)
        # Check that child columns exist
        assert len(row.children) >= 3

    def test_create_kpi_summary_cards_none_horizon(self):
        row = create_kpi_summary_cards(
            total_yards=1000.0,
            total_skeins=5.0,
            total_items=2,
            monthly_burn_rate=0.0,
            months_remaining=None,
        )
        assert isinstance(row, dbc.Row)

    def test_create_unit_selector_bar(self):
        bar = create_unit_selector_bar(active_unit="yards")
        assert isinstance(bar, (dbc.Card, dbc.Container, html.Div))

