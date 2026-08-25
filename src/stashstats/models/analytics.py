"""Analytics data models for stash flow, consumption velocity, and horizon projections."""

from datetime import datetime

from pydantic import BaseModel, Field


class StashDeltaEvent(BaseModel):
    """An atomic change event in stash quantity between two snapshots."""

    stash_id: int
    """Unique stash item database ID."""

    timestamp: str
    """Ravelry timestamp string of the event."""

    delta_skeins: float
    """Change in skeins (negative = consumed, positive = acquired)."""

    delta_grams: float = 0.0
    """Change in weight in grams."""

    delta_yards: float = 0.0
    """Change in length in yards."""

    event_type: str = "initial"
    """Classification: 'consumed' (delta < 0), 'acquired' (delta > 0), or 'initial'."""

    @property
    def datetime(self) -> datetime | None:
        """Parse timestamp string into timezone-aware datetime."""
        if not self.timestamp:
            return None
        try:
            return datetime.strptime(self.timestamp, "%Y/%m/%d %H:%M:%S %z")
        except ValueError:
            pass
        try:
            normalized = self.timestamp.replace("/", "-")
            return datetime.fromisoformat(normalized)
        except (ValueError, TypeError):
            return None


class PeriodicRollup(BaseModel):
    """Summary of stash flow over a calendar period (monthly or yearly)."""

    period: str
    """Period label (e.g. '2026-08' or '2026')."""

    acquired_yards: float = 0.0
    """Total yardage added to stash during period."""

    consumed_yards: float = 0.0
    """Total yardage consumed/knitted during period."""

    net_yards: float = 0.0
    """Net yardage change (acquired - consumed)."""

    acquired_skeins: float = 0.0
    """Total skeins added during period."""

    consumed_skeins: float = 0.0
    """Total skeins consumed during period."""

    net_skeins: float = 0.0
    """Net skein change (acquired - consumed)."""

    event_count: int = 0
    """Number of delta events recorded in this period."""


class RollingVelocity(BaseModel):
    """Trailing velocity metrics over a rolling day window."""

    window_days: int
    """Number of days in trailing window (e.g., 30, 90, 365)."""

    yards_consumed: float
    """Total yards consumed within this trailing window."""

    skeins_consumed: float
    """Total skeins consumed within this trailing window."""

    yards_per_day: float
    """Average daily knitting pace in yards."""

    yards_per_month: float
    """Estimated 30-day monthly burn rate (yards_per_day * 30.4375)."""

    skeins_per_month: float
    """Estimated monthly skein consumption rate."""


class StashHorizon(BaseModel):
    """Projection of stash depletion timeline."""

    total_active_yards: float
    """Current total yardage in active stash."""

    total_active_skeins: float
    """Current total skeins in active stash."""

    monthly_burn_rate_yards: float
    """Baseline monthly consumption rate used for projection."""

    months_remaining: float | None = None
    """Estimated months until stash depletion (None if burn rate is 0)."""

    years_remaining: float | None = None
    """Estimated years until stash depletion."""

    is_growing: bool = False
    """True if acquisition velocity exceeds consumption velocity."""


class StashVelocityReport(BaseModel):
    """Complete consumption velocity and stash flow report."""

    total_active_yards: float
    """Current active stash yardage."""

    total_active_skeins: float
    """Current active stash skeins."""

    total_active_items: int
    """Total count of items currently in stash."""

    periodic_monthly: list[PeriodicRollup] = Field(default_factory=list)
    """Monthly breakdown of acquisition and consumption."""

    periodic_yearly: list[PeriodicRollup] = Field(default_factory=list)
    """Yearly breakdown of acquisition and consumption."""

    velocity_30d: RollingVelocity | None = None
    """Rolling 30-day pace."""

    velocity_90d: RollingVelocity | None = None
    """Rolling 90-day pace."""

    velocity_365d: RollingVelocity | None = None
    """Rolling 365-day annual pace."""

    horizon: StashHorizon
    """Stash lifespan estimation."""


class ProjectUsageRecord(BaseModel):
    """Correlation record linking a stash item or yarn allocation to a project."""

    project_id: int
    """Ravelry project ID."""

    project_name: str
    """User project name."""

    pattern_name: str | None = None
    """Associated pattern title."""

    status_name: str | None = None
    """Project status (Finished, In progress, etc.)."""

    craft_name: str | None = None
    """Craft type (Knitting, Crochet, etc.)."""

    completed_date: str | None = None
    """Completion date if finished."""

    stash_id: int | None = None
    """Linked stash item ID."""

    yarn_name: str | None = None
    """Name or brand of the yarn used."""

    colorway: str | None = None
    """Colorway of the yarn pack."""

    skeins_used: float = 0.0
    """Skeins allocated to project."""

    yards_used: float = 0.0
    """Yards allocated to project."""

    meters_used: float = 0.0
    """Meters allocated to project."""

    grams_used: float = 0.0
    """Grams allocated to project."""


class ProjectConsumptionSummary(BaseModel):
    """Aggregate summary of projects made from stash."""

    project_usages: list[ProjectUsageRecord] = Field(default_factory=list)
    """Individual project-yarn usage links."""

    total_yards_consumed: float = 0.0
    """Total stash yards consumed in projects."""

    total_meters_consumed: float = 0.0
    """Total stash meters consumed in projects."""

    total_grams_consumed: float = 0.0
    """Total stash grams consumed in projects."""

    total_skeins_consumed: float = 0.0
    """Total stash skeins consumed in projects."""

    project_count: int = 0
    """Unique count of projects made from stash."""

