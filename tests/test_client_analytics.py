import json
from datetime import UTC, datetime
from unittest.mock import Mock, patch

import httpx
import pytest

from stashstats.client import RavelryClient
from stashstats.config import Settings
from stashstats.models.analytics import StashVelocityReport
from stashstats.models.common import Paginator
from stashstats.models.history import StashHistory, StashHistoryEntry
from stashstats.models.stash import StashItem, StashListResponse


@pytest.fixture
def mock_settings():
    return Settings(
        username="testuser",
        password="testpassword",
        base_url="https://api.ravelry.com",
    )


class TestClientAnalytics:
    def test_get_stash_velocity_report(self, mock_settings):
        client = RavelryClient(settings=mock_settings)
        client._cached_username = "testknitter"

        sample_items = [
            StashItem(
                id=10,
                name="Merino Classic",
                permalink="merino-classic",
                skeins=2.0,
                total_grams=200.0,
                total_yards=440.0,
            ),
            StashItem(
                id=20,
                name="Alpaca Silk",
                permalink="alpaca-silk",
                skeins=3.0,
                total_grams=150.0,
                total_yards=600.0,
            ),
        ]

        history_10 = StashHistory(
            stash_id=10,
            entries=[
                StashHistoryEntry(
                    timestamp="2026/06/01 10:00:00 +0000",
                    skeins=4.0,
                    total_grams=400.0,
                    total_yards=880.0,
                ),
                StashHistoryEntry(
                    timestamp="2026/08/01 10:00:00 +0000",
                    skeins=2.0,
                    total_grams=200.0,
                    total_yards=440.0,
                ),
            ],
        )
        history_20 = StashHistory(
            stash_id=20,
            entries=[
                StashHistoryEntry(
                    timestamp="2026/07/01 10:00:00 +0000",
                    skeins=3.0,
                    total_grams=150.0,
                    total_yards=600.0,
                ),
            ],
        )

        with patch.object(
            RavelryClient,
            "get_my_stash",
            return_value=StashListResponse(
                stash=sample_items,
                paginator=Paginator(page=1, page_size=50, page_count=1, total=2),
            ),
        ) as mock_get_stash, patch.object(
            RavelryClient,
            "get_batch_stash_history",
            return_value={10: history_10, 20: history_20},
        ) as mock_get_histories:
            report = client.get_stash_velocity_report(as_of=datetime(2026, 8, 15, tzinfo=UTC))

            mock_get_stash.assert_called_once_with(
                username=None,
                page=1,
                page_size=100,
                sort="created_",
                query=None,
                yarn_id=None,
                stash_status_id=None,
            )
            mock_get_histories.assert_called_once_with([10, 20], user_id=None)

            assert isinstance(report, StashVelocityReport)
            assert report.total_active_items == 2
            assert report.total_active_yards == 1040.0
            assert report.total_active_skeins == 5.0
            assert len(report.periodic_monthly) >= 2
            assert report.velocity_30d is not None
            assert report.horizon.total_active_yards == 1040.0
