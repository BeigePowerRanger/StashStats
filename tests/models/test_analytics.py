from datetime import UTC, datetime

from stashstats.models.analytics import (
    PeriodicRollup,
    RollingVelocity,
    StashDeltaEvent,
    StashHorizon,
    StashVelocityReport,
)


class TestStashDeltaEvent:
    def test_creation_and_properties(self):
        event = StashDeltaEvent(
            stash_id=12345,
            timestamp="2026/08/15 10:00:00 -0400",
            delta_skeins=-1.5,
            delta_grams=-150.0,
            delta_yards=-315.0,
            event_type="consumed",
        )
        assert event.stash_id == 12345
        assert event.delta_skeins == -1.5
        assert event.delta_grams == -150.0
        assert event.delta_yards == -315.0
        assert event.event_type == "consumed"

        dt = event.datetime
        assert dt is not None
        assert dt.year == 2026
        assert dt.month == 8
        assert dt.day == 15
        assert dt.tzinfo is not None

    def test_invalid_timestamp(self):
        event = StashDeltaEvent(
            stash_id=100,
            timestamp="invalid-time",
            delta_skeins=1.0,
            delta_grams=100.0,
            delta_yards=200.0,
            event_type="acquired",
        )
        assert event.datetime is None

    def test_iso_timestamp(self):
        event = StashDeltaEvent(
            stash_id=100,
            timestamp="2026-08-01T12:00:00+00:00",
            delta_skeins=2.0,
            delta_grams=200.0,
            delta_yards=400.0,
            event_type="acquired",
        )
        dt = event.datetime
        assert dt is not None
        assert dt.year == 2026
        assert dt.tzinfo == UTC


class TestPeriodicRollup:
    def test_defaults(self):
        rollup = PeriodicRollup(period="2026-08")
        assert rollup.period == "2026-08"
        assert rollup.acquired_yards == 0.0
        assert rollup.consumed_yards == 0.0
        assert rollup.net_yards == 0.0
        assert rollup.acquired_skeins == 0.0
        assert rollup.consumed_skeins == 0.0
        assert rollup.net_skeins == 0.0
        assert rollup.event_count == 0

    def test_populated_rollup(self):
        rollup = PeriodicRollup(
            period="2026-08",
            acquired_yards=800.0,
            consumed_yards=300.0,
            net_yards=500.0,
            acquired_skeins=4.0,
            consumed_skeins=1.5,
            net_skeins=2.5,
            event_count=3,
        )
        assert rollup.net_yards == 500.0
        assert rollup.event_count == 3


class TestRollingVelocity:
    def test_creation(self):
        velocity = RollingVelocity(
            window_days=30,
            yards_consumed=600.0,
            skeins_consumed=3.0,
            yards_per_day=20.0,
            yards_per_month=608.75,
            skeins_per_month=3.04,
        )
        assert velocity.window_days == 30
        assert velocity.yards_consumed == 600.0
        assert velocity.yards_per_day == 20.0
        assert velocity.yards_per_month == 608.75


class TestStashHorizon:
    def test_creation(self):
        horizon = StashHorizon(
            total_active_yards=2400.0,
            total_active_skeins=12.0,
            monthly_burn_rate_yards=600.0,
            months_remaining=4.0,
            years_remaining=0.33,
            is_growing=False,
        )
        assert horizon.total_active_yards == 2400.0
        assert horizon.months_remaining == 4.0
        assert horizon.years_remaining == 0.33
        assert horizon.is_growing is False


class TestStashVelocityReport:
    def test_creation(self):
        horizon = StashHorizon(
            total_active_yards=1000.0,
            total_active_skeins=5.0,
            monthly_burn_rate_yards=200.0,
            months_remaining=5.0,
            years_remaining=0.42,
        )
        report = StashVelocityReport(
            total_active_yards=1000.0,
            total_active_skeins=5.0,
            total_active_items=2,
            periodic_monthly=[PeriodicRollup(period="2026-08", consumed_yards=200.0, net_yards=-200.0)],
            periodic_yearly=[PeriodicRollup(period="2026", consumed_yards=200.0, net_yards=-200.0)],
            velocity_30d=RollingVelocity(
                window_days=30,
                yards_consumed=200.0,
                skeins_consumed=1.0,
                yards_per_day=6.67,
                yards_per_month=202.9,
                skeins_per_month=1.01,
            ),
            horizon=horizon,
        )
        assert report.total_active_yards == 1000.0
        assert len(report.periodic_monthly) == 1
        assert report.velocity_30d.yards_per_day == 6.67
        assert report.horizon.months_remaining == 5.0
