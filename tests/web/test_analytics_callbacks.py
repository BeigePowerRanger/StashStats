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
            "skeins": 3.0,
            "total_yards": 630.0,
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
            "skeins": 2.0,
            "total_yards": 880.0,
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
            "skeins": 1.0,
            "total_yards": 220.0,
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
        kpi, fiber_fig, weight_fig, flow_fig, vel_fig, w_val, c_val, s_val = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            selected_weights=None,
            selected_colors=None,
            search_query=None,
            reset_clicks=None,
            triggered_id=None,
        )

        assert isinstance(kpi, dbc.Row)
        assert isinstance(fiber_fig, go.Figure)
        assert isinstance(weight_fig, go.Figure)
        assert isinstance(flow_fig, go.Figure)
        assert isinstance(vel_fig, go.Figure)
        assert w_val is None
        assert c_val is None
        assert s_val is None

    def test_filter_by_weight(self):
        raw = sample_raw_stash()
        kpi, fiber_fig, weight_fig, flow_fig, vel_fig, w_val, c_val, s_val = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            selected_weights=["Worsted"],
            selected_colors=None,
            search_query=None,
            reset_clicks=None,
            triggered_id="analytics-filter-weight",
        )

        # Only 2 worsted items (total 850 yards)
        assert isinstance(weight_fig, go.Figure)
        assert list(weight_fig.data[0].x) == ["Worsted"]
        assert list(weight_fig.data[0].y) == [850.0]

    def test_filter_by_search_query(self):
        raw = sample_raw_stash()
        kpi, fiber_fig, weight_fig, flow_fig, vel_fig, w_val, c_val, s_val = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            selected_weights=None,
            selected_colors=None,
            search_query="Cascade",
            reset_clicks=None,
            triggered_id="analytics-filter-search",
        )

        assert list(weight_fig.data[0].y) == [220.0]

    def test_reset_filters(self):
        raw = sample_raw_stash()
        kpi, fiber_fig, weight_fig, flow_fig, vel_fig, w_val, c_val, s_val = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            selected_weights=["Worsted"],
            selected_colors=["Blue"],
            search_query="Cascade",
            reset_clicks=1,
            triggered_id="analytics-filter-reset",
        )

        assert w_val is None
        assert c_val is None
        assert s_val is None
        # All items restored (3 items)
        assert len(weight_fig.data[0].x) == 2
