from datetime import UTC, datetime, timedelta

from stashstats.analytics.velocity import StashVelocityCalculator
from stashstats.models.history import StashHistory, StashHistoryEntry
from stashstats.models.stash import StashItem


def create_sample_history(stash_id: int = 1) -> StashHistory:
    return StashHistory(
        stash_id=stash_id,
        entries=[
            StashHistoryEntry(
                timestamp="2026/06/01 10:00:00 +0000",
                skeins=4.0,
                total_grams=400.0,
                total_yards=800.0,
            ),
            StashHistoryEntry(
                timestamp="2026/07/01 10:00:00 +0000",
                skeins=3.0,
                total_grams=300.0,
                total_yards=600.0,
            ),
            StashHistoryEntry(
                timestamp="2026/08/01 10:00:00 +0000",
                skeins=1.0,
                total_grams=100.0,
                total_yards=200.0,
            ),
        ],
    )


class TestStashVelocityCalculator:
    def test_extract_events(self):
        history1 = create_sample_history(stash_id=1)
        history2 = StashHistory(
            stash_id=2,
            entries=[
                StashHistoryEntry(
                    timestamp="2026/07/15 12:00:00 +0000",
                    skeins=2.0,
                    total_grams=200.0,
                    total_yards=400.0,
                ),
                StashHistoryEntry(
                    timestamp="2026/08/10 12:00:00 +0000",
                    skeins=4.0,
                    total_grams=400.0,
                    total_yards=800.0,
                ),
            ],
        )

        histories = {1: history1, 2: history2}
        events = StashVelocityCalculator.extract_events(histories)

        # 3 events from history1 + 2 events from history2 = 5 events
        assert len(events) == 5

        # Check chronological order
        for i in range(len(events) - 1):
            assert events[i].datetime <= events[i + 1].datetime

        # Check consumption delta in history1
        consumed_events = [e for e in events if e.stash_id == 1 and e.event_type == "consumed"]
        assert len(consumed_events) == 2
        assert consumed_events[0].delta_yards == -200.0
        assert consumed_events[1].delta_yards == -400.0

        # Check acquisition delta in history2
        acquired_events = [e for e in events if e.stash_id == 2 and e.event_type == "acquired"]
        assert len(acquired_events) == 1
        assert acquired_events[0].delta_yards == 400.0

    def test_calculate_periodic_rollups_monthly(self):
        history = create_sample_history(stash_id=1)
        events = StashVelocityCalculator.extract_events({1: history})

        monthly_rollups = StashVelocityCalculator.calculate_periodic_rollups(events, granularity="monthly")
        assert len(monthly_rollups) == 3

        # June: Initial acquisition of 800 yds
        june = next(r for r in monthly_rollups if r.period == "2026-06")
        assert june.acquired_yards == 800.0
        assert june.consumed_yards == 0.0
        assert june.net_yards == 800.0

        # July: Consumed 200 yds
        july = next(r for r in monthly_rollups if r.period == "2026-07")
        assert july.acquired_yards == 0.0
        assert july.consumed_yards == 200.0
        assert july.net_yards == -200.0

        # August: Consumed 400 yds
        august = next(r for r in monthly_rollups if r.period == "2026-08")
        assert august.acquired_yards == 0.0
        assert august.consumed_yards == 400.0
        assert august.net_yards == -400.0

    def test_calculate_periodic_rollups_yearly(self):
        history = create_sample_history(stash_id=1)
        events = StashVelocityCalculator.extract_events({1: history})

        yearly_rollups = StashVelocityCalculator.calculate_periodic_rollups(events, granularity="yearly")
        assert len(yearly_rollups) == 1
        assert yearly_rollups[0].period == "2026"
        assert yearly_rollups[0].acquired_yards == 800.0
        assert yearly_rollups[0].consumed_yards == 600.0
        assert yearly_rollups[0].net_yards == 200.0

    def test_calculate_rolling_velocity(self):
        history = create_sample_history(stash_id=1)
        events = StashVelocityCalculator.extract_events({1: history})

        as_of = datetime(2026, 8, 15, tzinfo=UTC)

        # 30-day window covers 2026-07-16 to 2026-08-15 (covers 2026-08-01 event: 400 yards consumed)
        v30 = StashVelocityCalculator.calculate_rolling_velocity(events, window_days=30, as_of=as_of)
        assert v30.yards_consumed == 400.0
        assert v30.skeins_consumed == 2.0
        assert v30.yards_per_day == round(400.0 / 30.0, 2)

        # 90-day window covers 2026-07-01 and 2026-08-01 (covers 200 + 400 = 600 yards consumed)
        v90 = StashVelocityCalculator.calculate_rolling_velocity(events, window_days=90, as_of=as_of)
        assert v90.yards_consumed == 600.0
        assert v90.skeins_consumed == 3.0
        assert v90.yards_per_day == round(600.0 / 90.0, 2)

    def test_calculate_horizon(self):
        # 1200 yards active, burn rate 300 yds/month -> 4 months remaining
        horizon = StashVelocityCalculator.calculate_horizon(
            total_active_yards=1200.0,
            total_active_skeins=6.0,
            monthly_burn_rate_yards=300.0,
        )
        assert horizon.months_remaining == 4.0
        assert horizon.years_remaining == 0.33
        assert horizon.is_growing is False

        # Zero burn rate
        zero_horizon = StashVelocityCalculator.calculate_horizon(
            total_active_yards=1200.0,
            total_active_skeins=6.0,
            monthly_burn_rate_yards=0.0,
        )
        assert zero_horizon.months_remaining is None
        assert zero_horizon.years_remaining is None

    def test_generate_report(self):
        stash_item1 = StashItem(
            id=1,
            name="Merino Wool",
            permalink="merino-wool",
            skeins=1.0,
            total_grams=100.0,
            total_yards=200.0,
        )
        stash_item2 = StashItem(
            id=2,
            name="Silk Cloud",
            permalink="silk-cloud",
            skeins=4.0,
            total_grams=400.0,
            total_yards=800.0,
        )

        history1 = create_sample_history(stash_id=1)
        history2 = StashHistory(
            stash_id=2,
            entries=[
                StashHistoryEntry(
                    timestamp="2026/08/10 12:00:00 +0000",
                    skeins=4.0,
                    total_grams=400.0,
                    total_yards=800.0,
                )
            ],
        )

        report = StashVelocityCalculator.generate_report(
            stash_items=[stash_item1, stash_item2],
            histories={1: history1, 2: history2},
            as_of=datetime(2026, 8, 15, tzinfo=UTC),
        )

        assert report.total_active_items == 2
        assert report.total_active_yards == 1000.0
        assert report.total_active_skeins == 5.0
        assert len(report.periodic_monthly) >= 3
        assert report.velocity_30d is not None
        assert report.velocity_90d is not None
        assert report.horizon.total_active_yards == 1000.0
