import dash_bootstrap_components as dbc
from dash import html
import pytest

from stashstats.web.components.analytics import (
    create_analytics_filter_bar,
    create_kpi_summary_cards,
)


class TestAnalyticsComponents:
    def test_create_kpi_summary_cards(self):
        row = create_kpi_summary_cards(
            total_yards=3500.0,
            total_meters=3200.0,
            total_grams=1500.0,
            total_skeins=15.0,
            total_items=8,
            monthly_burn_rate=500.0,
            months_remaining=7.0,
            unit="yards",
        )
        assert isinstance(row, dbc.Row)
        assert len(row.children) >= 3

    def test_create_kpi_summary_cards_units(self):
        row_m = create_kpi_summary_cards(
            total_yards=3500.0,
            total_meters=3200.0,
            total_grams=1500.0,
            total_skeins=15.0,
            total_items=8,
            monthly_burn_rate=500.0,
            months_remaining=7.0,
            unit="meters",
        )
        assert isinstance(row_m, dbc.Row)

        row_g = create_kpi_summary_cards(
            total_yards=3500.0,
            total_meters=3200.0,
            total_grams=1500.0,
            total_skeins=15.0,
            total_items=8,
            monthly_burn_rate=500.0,
            months_remaining=7.0,
            unit="grams",
        )
        assert isinstance(row_g, dbc.Row)

        row_sk = create_kpi_summary_cards(
            total_yards=3500.0,
            total_meters=3200.0,
            total_grams=1500.0,
            total_skeins=15.0,
            total_items=8,
            monthly_burn_rate=500.0,
            months_remaining=7.0,
            unit="skeins",
        )
        assert isinstance(row_sk, dbc.Row)

    def test_create_kpi_summary_cards_none_horizon(self):
        row = create_kpi_summary_cards(
            total_yards=1000.0,
            total_meters=914.4,
            total_grams=400.0,
            total_skeins=5.0,
            total_items=2,
            monthly_burn_rate=0.0,
            months_remaining=None,
        )
        assert isinstance(row, dbc.Row)

    def test_create_analytics_filter_bar(self):
        filter_bar = create_analytics_filter_bar(
            color_families=["Blue", "Green", "Red"],
            active_unit="meters",
        )
        assert isinstance(filter_bar, (dbc.Card, dbc.Container, html.Div))
