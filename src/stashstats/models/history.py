from datetime import datetime

from pydantic import BaseModel, Field


class StashHistoryEntry(BaseModel):
    """Snapshot of stash yarn quantities at a specific point in time."""

    id: str | None = None
    """Unique entry identifier."""

    date: str | None = None
    """ISO date string (YYYY-MM-DD)."""

    timestamp: str = "" # TODO: needs to be validated as a proper Ravelry timestamp string (YYYY/MM/DD HH:MM:SS ±HHMM)
    """Ravelry timestamp string for the change event."""

    skeins: float # can't be negative, but can be zero
    """Number of skeins or delta skeins."""

    yards: float | None = None # can't be negative, but can be zero
    """Deducted or delta yards."""

    grams: float | None = None # can't be negative, but can be zero
    """Deducted or delta grams."""

    total_grams: float = 0.0
    """Total weight in grams at this point in time."""

    total_yards: float = 0.0
    """Total length in yards at this point in time."""

    pack_id: int | None = None
    """Associated pack record ID."""

    delta_skeins: float | None = None
    """Quantity delta recorded by this usage event (negative for deduction)."""

    notes: str | None = None
    """Optional project or usage event note."""

    project_id: int | None = None
    """Linked project ID if allocated to a project."""

    project_name: str | None = None
    """User-given project name."""

    pattern_name: str | None = None
    """Associated pattern name."""


    @property
    def datetime(self) -> datetime | None:
        """Parse the timestamp string into a datetime object."""
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


class StashHistory(BaseModel):
    """Historical timeline of quantity adjustments for a stash item."""

    stash_id: int
    """Associated stash item ID."""

    entries: list[StashHistoryEntry] = Field(default_factory=list)
    """Chronological list of history snapshots."""

