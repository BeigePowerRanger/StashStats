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
    ]


def sample_raw_projects() -> list[dict[str, Any]]:
    return [
        {
            "id": 501,
            "name": "Winter Beanie",
            "status_name": "Finished",
            "progress": 100,
            "craft_name": "Knitting",
            "pattern_name": "Classic Ribbed Hat",
            "completed": "2026-02-14",
            "packs": [
                {
                    "id": 1001,
                    "stash_id": 1,
                    "yarn_id": 101,
                    "colorway": "Azul Profundo",
                    "skeins": 1.5,
                    "total_yards": 315.0,
                    "total_meters": 288.0,
                    "total_grams": 150.0,
                }
            ],
        }
    ]


class TestAnalyticsCallbacks:
    def test_update_analytics_all_data(self):
        raw_stash = sample_raw_stash()
        raw_projects = sample_raw_projects()
        res = update_analytics_dashboard_logic(
            raw_stash_data=raw_stash,
            raw_projects_data=raw_projects,
            unit="yards",
        )
        kpi, fiber_fig, weight_fig, timeline_fig, flow_fig, vel_fig, proj_fig = res

        assert isinstance(kpi, dbc.Row)
        assert isinstance(fiber_fig, go.Figure)
        assert isinstance(weight_fig, go.Figure)
        assert isinstance(timeline_fig, go.Figure)
        assert isinstance(flow_fig, go.Figure)
        assert isinstance(vel_fig, go.Figure)
        assert isinstance(proj_fig, go.Figure)
        assert list(proj_fig.data[0].labels) == ["Winter Beanie"]

    def test_update_analytics_unit_meters(self):
        raw_stash = sample_raw_stash()
        raw_projects = sample_raw_projects()
        res = update_analytics_dashboard_logic(
            raw_stash_data=raw_stash,
            raw_projects_data=raw_projects,
            unit="meters",
        )
        weight_fig = res[2]
        assert "Meters" in weight_fig.layout.yaxis.title.text

    def test_update_analytics_unit_grams(self):
        raw_stash = sample_raw_stash()
        raw_projects = sample_raw_projects()
        res = update_analytics_dashboard_logic(
            raw_stash_data=raw_stash,
            raw_projects_data=raw_projects,
            unit="grams",
        )
        weight_fig = res[2]
        assert "Grams" in weight_fig.layout.yaxis.title.text

    def test_update_analytics_unit_skeins(self):
        raw_stash = sample_raw_stash()
        raw_projects = sample_raw_projects()
        res = update_analytics_dashboard_logic(
            raw_stash_data=raw_stash,
            raw_projects_data=raw_projects,
            unit="skeins",
        )
        weight_fig = res[2]
        assert "Skeins" in weight_fig.layout.yaxis.title.text

    def test_update_analytics_with_histories_data(self):
        raw_stash = sample_raw_stash()
        histories = {
            1: [
                {
                    "id": "entry-1",
                    "date": "2026-03-01",
                    "skeins": -1.0,
                    "yards": -210.0,
                    "grams": -100.0,
                    "project_name": "Cozy Scarf",
                    "pattern_name": "Ribbed Scarf",
                }
            ]
        }
        res = update_analytics_dashboard_logic(
            raw_stash_data=raw_stash,
            raw_projects_data=None,
            histories_data=histories,
            unit="yards",
        )
        flow_fig = res[4]
        proj_fig = res[6]

        assert isinstance(flow_fig, go.Figure)
        assert isinstance(proj_fig, go.Figure)
        assert "Cozy Scarf" in list(proj_fig.data[0].labels)

    def test_update_analytics_without_histories_or_projects(self):
        raw_stash = sample_raw_stash()
        res = update_analytics_dashboard_logic(
            raw_stash_data=raw_stash,
            raw_projects_data=None,
            histories_data=None,
            unit="yards",
        )
        flow_fig = res[4]
        assert isinstance(flow_fig, go.Figure)
        assert len(flow_fig.data) >= 1

