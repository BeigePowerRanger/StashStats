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
        kpi, fiber_fig, weight_fig, timeline_fig, flow_fig, projects_fig = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            raw_projects_data=None,
            histories_data=None,
            unit="yards",
        )

        assert isinstance(kpi, dbc.Row)
        assert isinstance(fiber_fig, go.Figure)
        assert isinstance(weight_fig, go.Figure)
        assert isinstance(timeline_fig, go.Figure)
        assert isinstance(flow_fig, go.Figure)
        assert isinstance(projects_fig, go.Figure)

    def test_update_analytics_unit_meters(self):
        raw = sample_raw_stash()
        kpi, fiber_fig, weight_fig, timeline_fig, flow_fig, projects_fig = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            unit="meters",
        )
        assert isinstance(kpi, dbc.Row)
        assert isinstance(weight_fig, go.Figure)

    def test_update_analytics_unit_grams(self):
        raw = sample_raw_stash()
        kpi, fiber_fig, weight_fig, timeline_fig, flow_fig, projects_fig = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            unit="grams",
        )
        assert isinstance(kpi, dbc.Row)

    def test_update_analytics_unit_skeins(self):
        raw = sample_raw_stash()
        kpi, fiber_fig, weight_fig, timeline_fig, flow_fig, projects_fig = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            unit="skeins",
        )
        assert isinstance(kpi, dbc.Row)

    def test_update_analytics_with_histories_data(self):
        raw = sample_raw_stash()
        histories = {
            1: [
                {
                    "event_type": "consumed",
                    "skeins": -1.0,
                    "yards": -210.0,
                    "grams": -100.0,
                    "project_name": "Cozy Scarf",
                    "pattern_name": "Ribbed Scarf",
                }
            ]
        }
        kpi, fiber_fig, weight_fig, timeline_fig, flow_fig, projects_fig = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            raw_projects_data=None,
            histories_data=histories,
            unit="yards",
        )
        assert isinstance(projects_fig, go.Figure)
        assert len(projects_fig.data) > 0

    def test_update_analytics_without_histories_or_projects(self):
        raw = sample_raw_stash()
        kpi, fiber_fig, weight_fig, timeline_fig, flow_fig, projects_fig = update_analytics_dashboard_logic(
            raw_stash_data=raw,
            raw_projects_data=None,
            histories_data=None,
            unit="yards",
        )
        assert isinstance(projects_fig, go.Figure)

