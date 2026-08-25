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

    def test_correlate_from_histories(self):
        stash = sample_stash_items()
        histories = {
            10: [
                {
                    "id": "entry-1",
                    "date": "2026-08-20",
                    "skeins": -1.5,
                    "yards": -315.0,
                    "grams": -150.0,
                    "project_name": "Autumn Beanie",
                    "project_id": 901,
                    "pattern_name": "Ribbed Watch Cap",
                }
            ]
        }
        records = StashProjectUsageCalculator.correlate_projects_and_stash(
            stash_items=stash,
            projects=[],
            histories=histories,
        )
        assert len(records) == 1
        assert records[0].project_name == "Autumn Beanie"
        assert records[0].project_id == 901
        assert records[0].pattern_name == "Ribbed Watch Cap"
        assert records[0].yards_used == 315.0
        assert records[0].skeins_used == 1.5
        assert records[0].stash_id == 10
        assert records[0].yarn_name == "Malabrigo Rios - Blue"

    def test_correlate_from_stash_item_packs(self):
        item = StashItem(
            id=30,
            name="Tosh Merino Light",
            permalink="tosh-merino-light",
            skeins=2.0,
            total_yards=840.0,
            packs=[
                Pack(
                    id=555,
                    project_id=888,
                    project_name="Pecan Hat",
                    colorway="Glazed Pecan",
                    skeins=1.0,
                    total_yards=420.0,
                    total_grams=100.0,
                )
            ],
        )
        records = StashProjectUsageCalculator.correlate_projects_and_stash([item])
        assert len(records) == 1
        assert records[0].project_id == 888
        assert records[0].project_name == "Pecan Hat"
        assert records[0].skeins_used == 1.0

    def test_generic_stash_usage_without_project_does_not_create_project(self):
        """Verify unlinked usage history without project_name or project_id does not create a fake project."""
        stash = sample_stash_items()
        histories = {
            10: [
                {
                    "event_type": "consumed",
                    "skeins": -1.0,
                    "yards": -210.0,
                    "grams": -100.0,
                    "project_name": None,
                    "project_id": None,
                    "notes": "Used some yarn for swatching",
                }
            ]
        }
        records = StashProjectUsageCalculator.correlate_projects_and_stash(
            stash_items=stash,
            histories=histories,
        )
        assert len(records) == 0

    def test_correlate_from_log_usage_with_custom_project_name(self):
        stash = sample_stash_items()
        histories = {
            10: [
                {
                    "skeins": -1.0,
                    "yards": -210.0,
                    "grams": -100.0,
                    "project_name": "Baby Goxzilla",
                    "pattern_name": "Nightshift",
                }
            ]
        }
        records = StashProjectUsageCalculator.correlate_projects_and_stash(
            stash_items=stash,
            histories=histories,
        )
        assert len(records) == 1
        assert records[0].project_name == "Baby Goxzilla"
        assert records[0].pattern_name == "Nightshift"
        assert records[0].skeins_used == 1.0
        assert records[0].yards_used == 210.0

    def test_new_stash_yarn_addition_does_not_create_project_usage(self):
        """Verify newly added stash items without logged usage never appear as projects."""
        new_yarn = StashItem(
            id=99,
            name="New Hedgehog Fibres Skinny Singles",
            permalink="new-hedgehog-fibres",
            colorway_name="Boombox",
            skeins=3.0,
            total_yards=1200.0,
            total_grams=300.0,
            packs=[
                Pack(
                    id=777,
                    colorway="Boombox",
                    skeins=3.0,
                    total_yards=1200.0,
                    total_grams=300.0,
                    project_id=None,
                    project_name=None,
                )
            ],
        )
        records = StashProjectUsageCalculator.correlate_projects_and_stash(
            stash_items=[new_yarn],
            projects=[],
            histories={
                99: [
                    {
                        "event_type": "initial",
                        "skeins": 3.0,
                        "yards": 1200.0,
                        "grams": 300.0,
                        "date": "2026-08-25",
                    }
                ]
            },
        )
        assert len(records) == 0

    def test_initial_history_entries_ignored(self):
        """Verify positive acquisition history entries are not treated as project usage."""
        stash = sample_stash_items()
        histories = {
            10: [
                {
                    "event_type": "initial",
                    "skeins": 2.0,
                    "yards": 420.0,
                    "grams": 200.0,
                    "date": "2026-01-01",
                }
            ],
            20: [
                {
                    "event_type": "acquired",
                    "delta_skeins": 3.0,
                    "delta_yards": 660.0,
                    "delta_grams": 300.0,
                    "date": "2026-01-01",
                }
            ],
        }
        records = StashProjectUsageCalculator.correlate_projects_and_stash(
            stash_items=stash,
            projects=[],
            histories=histories,
        )
        assert len(records) == 0





