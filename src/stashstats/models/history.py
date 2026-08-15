from datetime import datetime

from pydantic import BaseModel


class StashHistoryEntry(BaseModel):
    """Snapshot of stash yarn quantities at a specific point in time."""

    timestamp: str
    """Ravelry timestamp string for the change event."""

    skeins: float
    """Number of skeins in stash at this point in time."""

    total_grams: float
    """Total weight in grams at this point in time."""

    total_yards: float
    """Total length in yards at this point in time."""

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

    entries: list[StashHistoryEntry] = []
    """Chronological list of history snapshots."""
