# Implementation Plan: Stash Quantity History via Ravelry App Data API

## Goal Description
Track and persist quantity change history (`timestamp`, `skeins`, `total_grams`, `total_yards`) for stash items over time using Ravelry's App Data Key-Value storage API (`/app/data/get.json`, `/app/data/set.json`, `/app/data/delete.json`). 

This provides cloud-synced, multi-device history tracking without requiring an external database.

---

## Technical Specifications

### Key Namespace Convention
Each stash item's history is stored under key `stash_history_{stash_id}` in Ravelry's App Data key-value store.

### Payload Structure
```json
[
  {
    "timestamp": "2025/09/12 02:00:29 -0400",
    "skeins": 7.0,
    "total_grams": 700.0,
    "total_yards": 1379.0
  },
  {
    "timestamp": "2026/08/14 03:23:42 -0400",
    "skeins": 5.0,
    "total_grams": 500.0,
    "total_yards": 985.0
  }
]
```

### Auto-Deduplication
When recording history during updates or syncs, new entries are only appended if the timestamp or quantity values differ from the most recent entry.

---

## Architecture Flow

```mermaid
flowchart TD
    A[Stash Item Action: Create / Update / Sync] --> B[Extract Timestamp & Strict Quantity Metrics]
    B --> C[Fetch Existing History: GET /app/data/get.json?keys=stash_history_{id}]
    C --> D{Is Timestamp or Quantity New?}
    D -- Yes --> E[Append StashHistoryEntry to History List]
    E --> F[Persist: POST /app/data/set.json?stash_history_{id}=JSON]
    D -- No --> G[No-op / Skip Duplicate]
```

---

## Data Models (`src/stashstats/models/history.py`)

```python
from datetime import datetime
from pydantic import BaseModel


class StashHistoryEntry(BaseModel):
    """Snapshot of a stash item's quantity at a specific timestamp."""

    timestamp: str
    """Ravelry timestamp string (e.g. '2025/09/12 02:00:29 -0400')."""

    skeins: float
    """Number of skeins in stash at this point in time."""

    total_grams: float
    """Total grams in stash at this point in time."""

    total_yards: float
    """Total yardage in stash at this point in time."""

    @property
    def datetime(self) -> datetime | None:
        """Parsed timezone-aware datetime object."""
        try:
            return datetime.strptime(self.timestamp, "%Y/%m/%d %H:%M:%S %z")
        except (ValueError, TypeError):
            return None


class StashHistory(BaseModel):
    """Chronological revision history for a single stash item."""

    stash_id: int
    """Unique stash item database ID."""

    entries: list[StashHistoryEntry] = []
    """List of historical quantity snapshots in chronological order."""
```

---

## Client Methods (`src/stashstats/client.py`)
- `client.get_app_data(keys: list[str]) -> dict[str, str]`
- `client.set_app_data(**key_values: str) -> dict[str, str]`
- `client.delete_app_data(keys: list[str]) -> dict[str, str]`
- `client.get_stash_history(stash_id: int) -> StashHistory`
- `client.get_batch_stash_history(stash_ids: list[int]) -> dict[int, StashHistory]`
- `client.record_stash_snapshot(stash_item: StashItem, timestamp: str | None) -> StashHistory`
- `client.delete_stash_history(stash_id: int) -> dict[str, str]`
