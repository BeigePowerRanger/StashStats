from typing import Any
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pytest

from stashstats.web.callbacks.analytics import update_analytics_dashboard_logic


def sample_raw_stash() -> list[dict[str, Any]]:
    return [
        {
            "id": 1,
            "name": "Malabrigo Rios",
            "permalink": "malabrigo-rios",
            "colorway_name": "Azul Profundo",
            "color_family_name": "Blue",
            "yarn_weight_name": "Worsted",
            "created_at": "2026-01-10T00:00:00Z",
            "skeins": 3.0,
            "total_yards": 630.0,
            "total_meters": 576.0,
            "total_grams": 300.0,
            "yarn": {
                "id": 101,
                "name": "Rios",
                "yarn_company_name": "Malabrigo",
                "yarn_weight": {"id": 4, "name": "Worsted"},
            },
        },
        {
            "id": 2,
            "name": "Malabrigo Sock",
            "permalink": "malabrigo-sock",
            "colorway_name": "Lettuce",
            "color_family_name": "Green",
            "yarn_weight_name": "Fingering",
            "created_at": "2026-02-15T00:00:00Z",
            "skeins": 2.0,
            "total_yards": 880.0,
            "total_meters": 804.0,
            "total_grams": 200.0,
            "yarn": {
                "id": 102,
                "name": "Sock",
                "yarn_company_name": "Malabrigo",
                "yarn_weight": {"id": 1, "name": "Fingering"},
            },
        },
        {
            "id": 3,
            "name": "Cascade 220",
            "permalink": "cascade-220",
            "colorway_name": "Navy",
            "color_family_name": "Blue",
            "yarn_weight_name": "Worsted",
            "created_at": "2026-03-20T00:00:00Z",
            "skeins": 1.0,
            "total_yards": 220.0,
            "total_meters": 201.0,
            "total_grams": 100.0,
            "yarn": {
                "id": 103,
                "name": "220",
                "yarn_company_name": "Cascade Yarns",
                "yarn_weight": {"id": 4, "name": "Worsted"},
            },
        },
    ]


class TestAnalyticsCallbacks:
    def test_update_analytics_all_data(self):
        raw = sample_raw_stash()
        res = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            selected_colors=None,
            search_query=None,
            unit="yards",
            min_grams=None,
            max_grams=None,
            min_yards=None,
            max_yards=None,
            min_meters=None,
            max_meters=None,
            min_skeins=None,
            max_skeins=None,
            reset_clicks=None,
            triggered_id=None,
        )
        kpi, fiber_fig, weight_fig, timeline_fig, flow_fig, vel_fig = res[:6]

        assert isinstance(kpi, dbc.Row)
        assert isinstance(fiber_fig, go.Figure)
        assert isinstance(weight_fig, go.Figure)
        assert isinstance(timeline_fig, go.Figure)
        assert isinstance(flow_fig, go.Figure)
        assert isinstance(vel_fig, go.Figure)

    def test_update_analytics_unit_meters(self):
        raw = sample_raw_stash()
        res = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            selected_colors=None,
            search_query=None,
            unit="meters",
            min_grams=None,
            max_grams=None,
            min_yards=None,
            max_yards=None,
            min_meters=None,
            max_meters=None,
            min_skeins=None,
            max_skeins=None,
            reset_clicks=None,
            triggered_id="analytics-unit-selector",
        )
        weight_fig = res[2]
        assert "Meters" in weight_fig.layout.yaxis.title.text

    def test_update_analytics_unit_grams(self):
        raw = sample_raw_stash()
        res = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            selected_colors=None,
            search_query=None,
            unit="grams",
            min_grams=None,
            max_grams=None,
            min_yards=None,
            max_yards=None,
            min_meters=None,
            max_meters=None,
            min_skeins=None,
            max_skeins=None,
            reset_clicks=None,
            triggered_id="analytics-unit-selector",
        )
        weight_fig = res[2]
        assert "Grams" in weight_fig.layout.yaxis.title.text

    def test_update_analytics_unit_skeins(self):
        raw = sample_raw_stash()
        res = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            selected_colors=None,
            search_query=None,
            unit="skeins",
            min_grams=None,
            max_grams=None,
            min_yards=None,
            max_yards=None,
            min_meters=None,
            max_meters=None,
            min_skeins=None,
            max_skeins=None,
            reset_clicks=None,
            triggered_id="analytics-unit-selector",
        )
        weight_fig = res[2]
        assert "Skeins" in weight_fig.layout.yaxis.title.text

    def test_filter_by_color(self):
        raw = sample_raw_stash()
        res = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            selected_colors=["Green"],
            search_query=None,
            unit="yards",
            min_grams=None,
            max_grams=None,
            min_yards=None,
            max_yards=None,
            min_meters=None,
            max_meters=None,
            min_skeins=None,
            max_skeins=None,
            reset_clicks=None,
            triggered_id="analytics-filter-color",
        )
        weight_fig = res[2]

        # Only 1 green item (880 yards)
        assert isinstance(weight_fig, go.Figure)
        assert list(weight_fig.data[0].x) == ["Fingering"]
        assert list(weight_fig.data[0].y) == [880.0]

    def test_filter_by_grams(self):
        raw = sample_raw_stash()
        res = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            selected_colors=None,
            search_query=None,
            unit="yards",
            min_grams=250.0,
            max_grams=None,
            min_yards=None,
            max_yards=None,
            min_meters=None,
            max_meters=None,
            min_skeins=None,
            max_skeins=None,
            reset_clicks=None,
            triggered_id="analytics-filter-min-grams",
        )
        weight_fig = res[2]
        # Only item 1 (300g, 630 yards) matches
        assert list(weight_fig.data[0].y) == [630.0]

    def test_filter_by_yards(self):
        raw = sample_raw_stash()
        res = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            selected_colors=None,
            search_query=None,
            unit="yards",
            min_grams=None,
            max_grams=None,
            min_yards=700.0,
            max_yards=900.0,
            min_meters=None,
            max_meters=None,
            min_skeins=None,
            max_skeins=None,
            reset_clicks=None,
            triggered_id="analytics-filter-min-yards",
        )
        weight_fig = res[2]
        # Only item 2 (880 yards) matches
        assert list(weight_fig.data[0].x) == ["Fingering"]
        assert list(weight_fig.data[0].y) == [880.0]

    def test_filter_by_meters(self):
        raw = sample_raw_stash()
        res = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            selected_colors=None,
            search_query=None,
            unit="yards",
            min_grams=None,
            max_grams=None,
            min_yards=None,
            max_yards=None,
            min_meters=500.0,
            max_meters=600.0,
            min_skeins=None,
            max_skeins=None,
            reset_clicks=None,
            triggered_id="analytics-filter-min-meters",
        )
        weight_fig = res[2]
        # Only item 1 (576 meters, 630 yards) matches
        assert list(weight_fig.data[0].y) == [630.0]

    def test_filter_by_skeins(self):
        raw = sample_raw_stash()
        res = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            selected_colors=None,
            search_query=None,
            unit="yards",
            min_grams=None,
            max_grams=None,
            min_yards=None,
            max_yards=None,
            min_meters=None,
            max_meters=None,
            min_skeins=2.5,
            max_skeins=None,
            reset_clicks=None,
            triggered_id="analytics-filter-min-skeins",
        )
        weight_fig = res[2]
        # Only item 1 (3.0 skeins, 630 yards) matches
        assert list(weight_fig.data[0].y) == [630.0]

    def test_reset_filters_clears_quantities(self):
        raw = sample_raw_stash()
        res = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            selected_colors=["Blue"],
            search_query="Cascade",
            unit="meters",
            min_grams=100.0,
            max_grams=200.0,
            min_yards=200.0,
            max_yards=300.0,
            min_meters=150.0,
            max_meters=250.0,
            min_skeins=1.0,
            max_skeins=2.0,
            reset_clicks=1,
            triggered_id="analytics-filter-reset",
        )
        # Check that outputs return None for all filters and unit reset to "yards"
        (
            kpi,
            fiber_fig,
            weight_fig,
            timeline_fig,
            flow_fig,
            vel_fig,
            unit_val,
            c_val,
            s_val,
            min_g,
            max_g,
            min_y,
            max_y,
            min_m,
            max_m,
            min_sk,
            max_sk,
        ) = res

        assert unit_val == "yards"
        assert c_val is None
        assert s_val is None
        assert min_g is None
        assert max_g is None
        assert min_y is None
        assert max_y is None
        assert min_m is None
        assert max_m is None
        assert min_sk is None
        assert max_sk is None
        # All items restored (3 items)
        assert len(weight_fig.data[0].x) == 2
