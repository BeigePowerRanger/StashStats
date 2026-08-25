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
            unit="yards",
        )
        kpi, fiber_fig, weight_fig, timeline_fig, flow_fig, vel_fig = res

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
            unit="meters",
        )
        weight_fig = res[2]
        assert "Meters" in weight_fig.layout.yaxis.title.text

    def test_update_analytics_unit_grams(self):
        raw = sample_raw_stash()
        res = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            unit="grams",
        )
        weight_fig = res[2]
        assert "Grams" in weight_fig.layout.yaxis.title.text

    def test_update_analytics_unit_skeins(self):
        raw = sample_raw_stash()
        res = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            unit="skeins",
        )
        weight_fig = res[2]
        assert "Skeins" in weight_fig.layout.yaxis.title.text
