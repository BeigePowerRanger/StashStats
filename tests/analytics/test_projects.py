"""Unit tests for ProjectUsageRecord data model and StashProjectUsageCalculator."""

import pytest

from stashstats.analytics.projects import StashProjectUsageCalculator
from stashstats.models.analytics import ProjectConsumptionSummary, ProjectUsageRecord
from stashstats.models.common import Photo, YarnCompany
from stashstats.models.project import Project
from stashstats.models.stash import Pack, StashItem, StashYarn
from stashstats.models.yarn import YarnWeight


def sample_stash_items() -> list[StashItem]:
    return [
        StashItem(
            id=10,
            name="Malabrigo Rios - Blue",
            permalink="malabrigo-rios-blue",
            colorway_name="Azul Profundo",
            yarn_weight_name="Worsted",
            skeins=2.0,
            total_yards=420.0,
            total_meters=384.0,
            total_grams=200.0,
            yarn=StashYarn(
                id=101,
                name="Rios",
                yarn_company_name="Malabrigo",
                yarn_company=YarnCompany(id=1, name="Malabrigo"),
                yarn_weight=YarnWeight(id=4, name="Worsted"),
            ),
        ),
        StashItem(
            id=20,
            name="Cascade 220 - Grey",
            permalink="cascade-220-grey",
            colorway_name="Silver",
            yarn_weight_name="Worsted",
            skeins=3.0,
            total_yards=660.0,
            total_meters=603.0,
            total_grams=300.0,
            yarn=StashYarn(
                id=102,
                name="220",
                yarn_company_name="Cascade Yarns",
                yarn_company=YarnCompany(id=2, name="Cascade Yarns"),
                yarn_weight=YarnWeight(id=4, name="Worsted"),
            ),
        ),
    ]


def sample_projects() -> list[Project]:
    return [
        Project(
            id=501,
            name="Winter Beanie",
            status_name="Finished",
            progress=100,
            craft_name="Knitting",
            pattern_name="Classic Ribbed Hat",
            completed="2026-02-14",
            packs=[
                Pack(
                    id=1001,
                    stash_id=10,
                    yarn_id=101,
                    colorway="Azul Profundo",
                    skeins=1.5,
                    total_yards=315.0,
                    total_meters=288.0,
                    total_grams=150.0,
                )
            ],
        ),
        Project(
            id=502,
            name="Cozy Cowl",
            status_name="In progress",
            progress=60,
            craft_name="Knitting",
            pattern_name="Honey Cowl",
            completed=None,
            packs=[
                Pack(
                    id=1002,
                    stash_id=10,
                    yarn_id=101,
                    colorway="Azul Profundo",
                    skeins=0.5,
                    total_yards=105.0,
                    total_meters=96.0,
                    total_grams=50.0,
                ),
                Pack(
                    id=1003,
                    stash_id=20,
                    yarn_id=102,
                    colorway="Silver",
                    skeins=2.0,
                    total_yards=440.0,
                    total_meters=402.0,
                    total_grams=200.0,
                ),
            ],
        ),
    ]


class TestStashProjectUsageCalculator:
    def test_correlate_projects_and_stash(self):
        stash = sample_stash_items()
        projects = sample_projects()

        records = StashProjectUsageCalculator.correlate_projects_and_stash(stash, projects)
        assert len(records) == 3

        # Record 1: Winter Beanie using Rios
        beanie_record = next(r for r in records if r.project_id == 501 and r.stash_id == 10)
        assert beanie_record.project_name == "Winter Beanie"
        assert beanie_record.pattern_name == "Classic Ribbed Hat"
        assert beanie_record.status_name == "Finished"
        assert beanie_record.completed_date == "2026-02-14"
        assert beanie_record.yarn_name == "Malabrigo Rios - Blue"
        assert beanie_record.skeins_used == 1.5
        assert beanie_record.yards_used == 315.0
        assert beanie_record.meters_used == 288.0
        assert beanie_record.grams_used == 150.0

        # Record 2 & 3: Cozy Cowl using Rios & Cascade 220
        cowl_rios = next(r for r in records if r.project_id == 502 and r.stash_id == 10)
        assert cowl_rios.yards_used == 105.0

        cowl_cascade = next(r for r in records if r.project_id == 502 and r.stash_id == 20)
        assert cowl_cascade.yards_used == 440.0

    def test_aggregate_summary(self):
        stash = sample_stash_items()
        projects = sample_projects()

        records = StashProjectUsageCalculator.correlate_projects_and_stash(stash, projects)
        summary = StashProjectUsageCalculator.aggregate_summary(records)

        assert isinstance(summary, ProjectConsumptionSummary)
        assert summary.project_count == 2
        assert summary.total_yards_consumed == 315.0 + 105.0 + 440.0
        assert summary.total_skeins_consumed == 1.5 + 0.5 + 2.0
        assert summary.total_grams_consumed == 150.0 + 50.0 + 200.0

    def test_get_projects_for_stash_item(self):
        stash = sample_stash_items()
        projects = sample_projects()

        records = StashProjectUsageCalculator.correlate_projects_and_stash(stash, projects)
        item10_projects = StashProjectUsageCalculator.get_projects_for_stash_item(10, records)

        assert len(item10_projects) == 2
        assert {p.project_name for p in item10_projects} == {"Winter Beanie", "Cozy Cowl"}

        item20_projects = StashProjectUsageCalculator.get_projects_for_stash_item(20, records)
        assert len(item20_projects) == 1
        assert item20_projects[0].project_name == "Cozy Cowl"

    def test_empty_correlation(self):
        records = StashProjectUsageCalculator.correlate_projects_and_stash([], [])
        assert records == []

        summary = StashProjectUsageCalculator.aggregate_summary([])
        assert summary.project_count == 0
        assert summary.total_yards_consumed == 0.0
