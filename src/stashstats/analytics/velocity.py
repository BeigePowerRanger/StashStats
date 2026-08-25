"""Stash consumption velocity, rollups, and lifespan horizon calculation engine."""

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import Any


from stashstats.models.analytics import (
    PeriodicRollup,
    RollingVelocity,
    StashDeltaEvent,
    StashHorizon,
    StashVelocityReport,
)
from stashstats.models.history import StashHistory
from stashstats.models.stash import StashItem


class StashVelocityCalculator:
    """Computes delta events, periodic rollups, and rolling velocities from stash histories."""

    @classmethod
    def extract_events(
        cls,
        histories: dict[int, Any] | None = None,
        stash_items: list[StashItem] | None = None,
    ) -> list[StashDeltaEvent]:
        """Extract chronological delta events across all stash histories and items.

        Args:
            histories: Mapping of stash_id to StashHistory container or list of entries.
            stash_items: Optional list of StashItem records to synthesize baseline events when histories are missing.

        Returns:
            Sorted list of StashDeltaEvent instances.
        """
        all_events: list[StashDeltaEvent] = []
        covered_stash_ids: set[int] = set()

        # 1. Process explicit history records
        if histories:
            for stash_id, history in histories.items():
                entries = getattr(history, "entries", None) if hasattr(history, "entries") else (history if isinstance(history, list) else [])
                if not entries:
                    continue

                covered_stash_ids.add(stash_id)

                # Sort entries chronologically
                sorted_entries = sorted(
                    entries,
                    key=lambda e: (e.datetime if hasattr(e, "datetime") else None)
                    or (datetime.fromisoformat(e["date"]).replace(tzinfo=UTC) if isinstance(e, dict) and e.get("date") else None)
                    or datetime.min.replace(tzinfo=UTC),
                )

                # First entry is initial baseline acquisition
                initial_entry = sorted_entries[0]
                initial_skeins = initial_entry.skeins if hasattr(initial_entry, "skeins") else initial_entry.get("skeins", 0.0)
                initial_grams = (
                    (initial_entry.total_grams or initial_entry.grams or 0.0)
                    if hasattr(initial_entry, "total_grams")
                    else (initial_entry.get("total_grams") or initial_entry.get("grams") or 0.0)
                )
                initial_yards = (
                    (initial_entry.total_yards or initial_entry.yards or 0.0)
                    if hasattr(initial_entry, "total_yards")
                    else (initial_entry.get("total_yards") or initial_entry.get("yards") or 0.0)
                )
                initial_ts = (
                    initial_entry.timestamp
                    if hasattr(initial_entry, "timestamp")
                    else (initial_entry.get("timestamp") or initial_entry.get("date"))
                )

                all_events.append(
                    StashDeltaEvent(
                        stash_id=stash_id,
                        timestamp=initial_ts,
                        delta_skeins=initial_skeins or 0.0,
                        delta_grams=initial_grams or 0.0,
                        delta_yards=initial_yards or 0.0,
                        event_type="initial",
                    )
                )

                # Subsequent transitions are deltas
                for i in range(1, len(sorted_entries)):
                    prev = sorted_entries[i - 1]
                    curr = sorted_entries[i]

                    prev_grams = (prev.total_grams or prev.grams or 0.0) if hasattr(prev, "total_grams") else (prev.get("total_grams") or prev.get("grams") or 0.0)
                    curr_grams = (curr.total_grams or curr.grams or 0.0) if hasattr(curr, "total_grams") else (curr.get("total_grams") or curr.get("grams") or 0.0)
                    prev_yards = (prev.total_yards or prev.yards or 0.0) if hasattr(prev, "total_yards") else (prev.get("total_yards") or prev.get("yards") or 0.0)
                    curr_yards = (curr.total_yards or curr.yards or 0.0) if hasattr(curr, "total_yards") else (curr.get("total_yards") or curr.get("yards") or 0.0)
                    prev_skeins = prev.skeins if hasattr(prev, "skeins") else prev.get("skeins", 0.0)
                    curr_skeins = curr.skeins if hasattr(curr, "skeins") else curr.get("skeins", 0.0)
                    curr_ts = curr.timestamp if hasattr(curr, "timestamp") else (curr.get("timestamp") or curr.get("date"))

                    delta_skeins = curr_skeins - prev_skeins
                    delta_grams = curr_grams - prev_grams
                    delta_yards = curr_yards - prev_yards

                    event_type = (
                        "consumed"
                        if delta_yards < 0 or delta_skeins < 0
                        else ("acquired" if delta_yards > 0 or delta_skeins > 0 else "neutral")
                    )

                    all_events.append(
                        StashDeltaEvent(
                            stash_id=stash_id,
                            timestamp=curr_ts,
                            delta_skeins=delta_skeins,
                            delta_grams=delta_grams,
                            delta_yards=delta_yards,
                            event_type=event_type,
                        )
                    )

        # 2. Synthesize baseline acquisition & consumption events for stash items not in histories
        if stash_items:
            for item in stash_items:
                if item.id and item.id in covered_stash_ids:
                    continue

                ts = item.created_at or datetime.now(tz=UTC).strftime("%Y/%m/%d %H:%M:%S +0000")
                initial_skeins = item.skeins or 0.0
                initial_yards = item.total_yards or 0.0
                initial_grams = item.total_grams or 0.0

                all_events.append(
                    StashDeltaEvent(
                        stash_id=item.id or 0,
                        timestamp=ts,
                        delta_skeins=initial_skeins,
                        delta_grams=initial_grams,
                        delta_yards=initial_yards,
                        event_type="initial",
                    )
                )

        # Sort all events globally by datetime
        return sorted(
            all_events,
            key=lambda e: e.datetime or datetime.min.replace(tzinfo=UTC),
        )

    @staticmethod
    def calculate_periodic_rollups(
        events: list[StashDeltaEvent],
        granularity: str = "monthly",
    ) -> list[PeriodicRollup]:
        """Aggregate delta events into periodic calendar intervals (monthly or yearly).

        Args:
            events: List of StashDeltaEvent instances.
            granularity: 'monthly' (YYYY-MM) or 'yearly' (YYYY).

        Returns:
            List of PeriodicRollup summaries sorted chronologically.
        """
        grouped_events: dict[str, list[StashDeltaEvent]] = defaultdict(list)

        for event in events:
            dt = event.datetime
            if dt is None:
                continue

            period_key = dt.strftime("%Y-%m" if granularity == "monthly" else "%Y")
            grouped_events[period_key].append(event)

        rollups: list[PeriodicRollup] = []
        for period in sorted(grouped_events.keys()):
            period_group = grouped_events[period]

            acquired_yds = sum(e.delta_yards for e in period_group if e.delta_yards > 0)
            consumed_yds = sum(abs(e.delta_yards) for e in period_group if e.delta_yards < 0)
            acquired_sk = sum(e.delta_skeins for e in period_group if e.delta_skeins > 0)
            consumed_sk = sum(abs(e.delta_skeins) for e in period_group if e.delta_skeins < 0)

            rollups.append(
                PeriodicRollup(
                    period=period,
                    acquired_yards=round(acquired_yds, 2),
                    consumed_yards=round(consumed_yds, 2),
                    net_yards=round(acquired_yds - consumed_yds, 2),
                    acquired_skeins=round(acquired_sk, 2),
                    consumed_skeins=round(consumed_sk, 2),
                    net_skeins=round(acquired_sk - consumed_sk, 2),
                    event_count=len(period_group),
                )
            )

        return rollups

    @staticmethod
    def calculate_rolling_velocity(
        events: list[StashDeltaEvent],
        window_days: int,
        as_of: datetime | None = None,
    ) -> RollingVelocity:
        """Calculate consumption velocity across a trailing N-day window.

        Args:
            events: List of StashDeltaEvent instances.
            window_days: Window duration in days (e.g., 30, 90, 365).
            as_of: Benchmark date for trailing window (defaults to now in UTC).

        Returns:
            RollingVelocity metrics instance.
        """
        if as_of is None:
            as_of = datetime.now(UTC)
        elif as_of.tzinfo is None:
            as_of = as_of.replace(tzinfo=UTC)

        cutoff = as_of - timedelta(days=window_days)

        window_events = [
            e
            for e in events
            if e.datetime is not None and cutoff <= e.datetime <= as_of
        ]

        yards_consumed = sum(abs(e.delta_yards) for e in window_events if e.delta_yards < 0)
        skeins_consumed = sum(abs(e.delta_skeins) for e in window_events if e.delta_skeins < 0)

        effective_days = max(1, window_days)
        yards_per_day = round(yards_consumed / effective_days, 2)
        yards_per_month = round(yards_per_day * 30.4375, 2)
        skeins_per_month = round((skeins_consumed / effective_days) * 30.4375, 2)

        return RollingVelocity(
            window_days=window_days,
            yards_consumed=round(yards_consumed, 2),
            skeins_consumed=round(skeins_consumed, 2),
            yards_per_day=yards_per_day,
            yards_per_month=yards_per_month,
            skeins_per_month=skeins_per_month,
        )

    @staticmethod
    def calculate_horizon(
        total_active_yards: float,
        total_active_skeins: float,
        monthly_burn_rate_yards: float,
        net_inflow_rate_yards: float = 0.0,
    ) -> StashHorizon:
        """Project stash lifespan horizon based on active inventory and burn rate.

        Args:
            total_active_yards: Total yards currently in stash.
            total_active_skeins: Total skeins currently in stash.
            monthly_burn_rate_yards: Average monthly consumption rate in yards.
            net_inflow_rate_yards: Net monthly acquisition rate in yards.

        Returns:
            StashHorizon projection.
        """
        if monthly_burn_rate_yards <= 0.0:
            return StashHorizon(
                total_active_yards=round(total_active_yards, 2),
                total_active_skeins=round(total_active_skeins, 2),
                monthly_burn_rate_yards=0.0,
                months_remaining=None,
                years_remaining=None,
                is_growing=net_inflow_rate_yards > 0,
            )

        months_remaining = round(total_active_yards / monthly_burn_rate_yards, 2)
        years_remaining = round(months_remaining / 12.0, 2)
        is_growing = net_inflow_rate_yards > monthly_burn_rate_yards

        return StashHorizon(
            total_active_yards=round(total_active_yards, 2),
            total_active_skeins=round(total_active_skeins, 2),
            monthly_burn_rate_yards=round(monthly_burn_rate_yards, 2),
            months_remaining=months_remaining,
            years_remaining=years_remaining,
            is_growing=is_growing,
        )

    @classmethod
    def generate_report(
        cls,
        stash_items: list[StashItem],
        histories: dict[int, StashHistory],
        as_of: datetime | None = None,
    ) -> StashVelocityReport:
        """Generate composite stash flow and consumption velocity report.

        Args:
            stash_items: List of active user stash items.
            histories: Mapping of stash item IDs to quantity histories.
            as_of: Benchmark date for trailing velocity (defaults to now in UTC).

        Returns:
            StashVelocityReport composite report.
        """
        total_active_yards = sum(
            (getattr(item, "yards_remaining", None) if getattr(item, "yards_remaining", None) is not None else item.total_yards) or 0.0
            for item in stash_items
        )
        total_active_skeins = sum(
            (getattr(item, "skeins_remaining", None) if getattr(item, "skeins_remaining", None) is not None else item.skeins) or 0.0
            for item in stash_items
        )
        total_active_items = len(stash_items)

        events = cls.extract_events(histories=histories, stash_items=stash_items)
        periodic_monthly = cls.calculate_periodic_rollups(events, granularity="monthly")
        periodic_yearly = cls.calculate_periodic_rollups(events, granularity="yearly")

        velocity_30d = cls.calculate_rolling_velocity(events, window_days=30, as_of=as_of)
        velocity_90d = cls.calculate_rolling_velocity(events, window_days=90, as_of=as_of)
        velocity_365d = cls.calculate_rolling_velocity(events, window_days=365, as_of=as_of)

        # Baseline burn rate priority: 90d -> 30d -> 365d -> 0.0
        monthly_burn_rate = (
            velocity_90d.yards_per_month
            if velocity_90d.yards_per_month > 0
            else (velocity_30d.yards_per_month if velocity_30d.yards_per_month > 0 else velocity_365d.yards_per_month)
        )

        horizon = cls.calculate_horizon(
            total_active_yards=total_active_yards,
            total_active_skeins=total_active_skeins,
            monthly_burn_rate_yards=monthly_burn_rate,
        )

        return StashVelocityReport(
            total_active_yards=round(total_active_yards, 2),
            total_active_skeins=round(total_active_skeins, 2),
            total_active_items=total_active_items,
            periodic_monthly=periodic_monthly,
            periodic_yearly=periodic_yearly,
            velocity_30d=velocity_30d,
            velocity_90d=velocity_90d,
            velocity_365d=velocity_365d,
            horizon=horizon,
        )
