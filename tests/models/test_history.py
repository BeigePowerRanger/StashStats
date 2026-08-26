from datetime import UTC

import pytest
from pydantic import ValidationError

from stashstats.models.history import StashHistory, StashHistoryEntry


class TestStashHistoryEntry:
    def test_ravelry_timestamp_parsing(self):
        entry = StashHistoryEntry(
            timestamp="2024/05/15 14:30:00 -0400",
            skeins=4.0,
            total_grams=400.0,
            total_yards=840.0,
        )
        dt = entry.datetime
        assert dt is not None
        assert dt.year == 2024
        assert dt.month == 5
        assert dt.day == 15
        assert dt.hour == 14
        assert dt.minute == 30
        assert dt.tzinfo is not None
        # -04:00 is -14400 seconds
        assert dt.utcoffset().total_seconds() == -14400

    def test_iso_timestamp_parsing(self):
        entry = StashHistoryEntry(
            timestamp="2024-06-01T12:00:00+00:00",
            skeins=2.0,
            total_grams=200.0,
            total_yards=420.0,
        )
        dt = entry.datetime
        assert dt is not None
        assert dt.year == 2024
        assert dt.month == 6
        assert dt.day == 1
        assert dt.hour == 12
        assert dt.tzinfo == UTC

    def test_slash_iso_hybrid_timestamp(self):
        entry = StashHistoryEntry(
            timestamp="2024/06/01T12:00:00+00:00",
            skeins=2.0,
            total_grams=200.0,
            total_yards=420.0,
        )
        dt = entry.datetime
        assert dt is not None
        assert dt.year == 2024
        assert dt.month == 6

    def test_invalid_timestamp(self):
        with pytest.raises(ValidationError):
            StashHistoryEntry(
                timestamp="not-a-timestamp",
                skeins=1.0,
                total_grams=100.0,
                total_yards=200.0,
            )

    def test_entry_with_project_metadata(self):
        entry = StashHistoryEntry(
            timestamp="2026/08/24 12:00:00 +0000",
            skeins=0.0,
            delta_skeins=-1.5,
            yards=315.0,
            grams=150.0,
            project_id=501,
            project_name="Winter Beanie",
            pattern_name="Classic Ribbed Hat",
            notes="Knitted with stash yarn",
        )
        assert entry.project_id == 501
        assert entry.project_name == "Winter Beanie"
        assert entry.pattern_name == "Classic Ribbed Hat"
        assert entry.delta_skeins == -1.5

    def test_empty_timestamp(self):
        entry = StashHistoryEntry(
            timestamp="",
            skeins=1.0,
            total_grams=100.0,
            total_yards=200.0,
        )
        assert entry.datetime is None


class TestStashHistory:
    def test_stash_history_container(self):
        history = StashHistory(
            stash_id=999,
            entries=[
                StashHistoryEntry(
                    timestamp="2024/01/01 10:00:00 +0000",
                    skeins=5.0,
                    total_grams=500.0,
                    total_yards=1050.0,
                ),
                StashHistoryEntry(
                    timestamp="2024/02/01 10:00:00 +0000",
                    skeins=3.0,
                    total_grams=300.0,
                    total_yards=630.0,
                ),
            ],
        )
        assert history.stash_id == 999
        assert len(history.entries) == 2
        assert history.entries[0].skeins == 5.0
        assert history.entries[1].skeins == 3.0
        assert history.entries[0].datetime < history.entries[1].datetime

    def test_empty_stash_history(self):
        history = StashHistory(stash_id=100)
        assert history.stash_id == 100
        assert history.entries == []
