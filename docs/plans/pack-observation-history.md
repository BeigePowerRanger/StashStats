# Plan: Lean Stash History via Pack Observation

## Goal Description

Ravelry already stores every quantity update as a distinct **Pack** record. When you update skeins,
Ravelry does not overwrite the pack — it creates a new pack linked to the primary via `primary_pack_id`.

```
Pack 134290871  primary_pack_id=null   skeins=7.0   ← current / primary
Pack 134290872  primary_pack_id=134290871  skeins=5.5  ← revision
Pack 135830458  primary_pack_id=134290871  skeins=1.0  ← revision
Pack 135882039  primary_pack_id=134290871  skeins=0.5  ← revision
```

However, **packs have no timestamp**. The only timestamp on the stash item is `updated_at`, which
reflects the most recent change only.

**The plan**: Replace the current `StashHistory` / `StashHistoryEntry` system (which was redundantly
duplicating `skeins`, `total_grams`, `total_yards` into App Data) with a lean **pack observation
log** that stores only `{pack_id, observed_at}` pairs. Quantity data is resolved live from the API
using those pack IDs when needed — no duplication, smaller payloads, correct source of truth.

---

## User Review Required

> [!IMPORTANT]
> **Breaking change to existing App Data keys.** Any `stash_history_*` keys already stored in
> Ravelry App Data use the old format (`skeins`, `total_grams`, `total_yards` entries). These will
> be unreadable by the new model. The plan includes a **migration helper** to either delete old keys
> or re-write them. Since testing was done against a live account, old test keys may already exist
> and should be cleaned up.

> [!WARNING]
> **Packs have no individual timestamps.** We can only record *when we first observed* each pack
> (i.e. the time of the API call or the stash `updated_at` at the moment of the update). This is
> inherently approximate — not a perfect audit log — but it is the best the Ravelry API allows.

---

## Open Questions

None — approach agreed during brainstorming.

---

## Proposed Changes

### Component 1: `models/history.py`

Replace current `StashHistoryEntry` / `StashHistory` with two new models.

#### [MODIFY] `history.py`

```diff
- class StashHistoryEntry(BaseModel):
-     timestamp: str
-     skeins: float
-     total_grams: float
-     total_yards: float
-     @property def datetime(self) -> datetime | None: ...

- class StashHistory(BaseModel):
-     stash_id: int
-     entries: list[StashHistoryEntry] = []

+ class PackObservation(BaseModel):
+     """A single observed pack state — links a pack ID to the timestamp we first saw it."""
+
+     pack_id: int
+     """Ravelry pack database ID."""
+
+     observed_at: str
+     """Timestamp string when this pack was first observed (from stash updated_at or now())."""
+
+     @property
+     def datetime(self) -> datetime | None:
+         """Parse observed_at into a timezone-aware datetime."""
+         ...

+ class StashPackHistory(BaseModel):
+     """Chronological log of pack observations for a single stash item."""
+
+     stash_id: int
+     """Associated stash item ID."""
+
+     observations: list[PackObservation] = []
+     """Ordered list of pack observations, oldest first."""
```

**Note:** The old `StashHistory` and `StashHistoryEntry` names are removed. `StashPackHistory` and
`PackObservation` replace them in all exports.

---

### Component 2: `models/__init__.py`

#### [MODIFY] `__init__.py`

```diff
- from stashstats.models.history import StashHistory, StashHistoryEntry
+ from stashstats.models.history import StashPackHistory, PackObservation

  __all__ = [
-     "StashHistory",
-     "StashHistoryEntry",
+     "StashPackHistory",
+     "PackObservation",
      ...
  ]
```

---

### Component 3: `src/stashstats/__init__.py`

#### [MODIFY] `__init__.py` (package root)

Same rename: replace `StashHistory`, `StashHistoryEntry` with `StashPackHistory`, `PackObservation`
in imports and `__all__`.

---

### Component 4: `client.py` — History Methods

All history-related methods are rewritten. The key-naming convention (`stash_history_{id}`) stays
the same so future migration is possible.

#### [MODIFY] `client.py`

**Imports:**
```diff
- from stashstats.models import StashHistory, StashHistoryEntry, StashItem, ...
+ from stashstats.models import StashPackHistory, PackObservation, StashItem, ...
```

**`_load_pack_history(stash_id)` — internal helper (replaces `get_stash_history`):**
```python
def _load_pack_history(self, stash_id: int) -> StashPackHistory:
    """Load pack observation log from App Data for a stash item."""
    key = self._stash_history_key(stash_id)
    app_data = self.get_app_data([key])
    raw = app_data.get(key)
    if not raw:
        return StashPackHistory(stash_id=stash_id)
    try:
        parsed = json.loads(raw) if isinstance(raw, str) else raw
    except json.JSONDecodeError:
        return StashPackHistory(stash_id=stash_id)
    return StashPackHistory.model_validate(parsed)
```

**`get_stash_pack_history(stash_id)` — public getter:**
```python
def get_stash_pack_history(self, stash_id: int) -> StashPackHistory:
    """Retrieve the pack observation log for a stash item."""
    ...
```

**`get_batch_stash_pack_history(stash_ids)` — batch getter:**
```python
def get_batch_stash_pack_history(self, stash_ids: list[int]) -> dict[int, StashPackHistory]:
    """Retrieve pack histories for multiple stash items in a single App Data request."""
    ...
```

**`record_pack_observation(stash_item, pack_id, observed_at)` — replaces `record_stash_snapshot`:**
```python
def record_pack_observation(
    self,
    stash_item: StashItem,
    pack_id: int | None = None,
    observed_at: str | None = None,
) -> StashPackHistory:
    """Record a pack observation entry when a stash item is created or updated.

    Resolves pack_id from stash_item.primary_pack if not provided.
    Resolves observed_at from stash_item.updated_at if not provided.
    Skips if pack_id is already present in the observation log (deduplication).
    """
    resolved_pack_id = pack_id
    if resolved_pack_id is None:
        pack = stash_item.primary_pack or (stash_item.packs[0] if stash_item.packs else None)
        if pack is None:
            return self._load_pack_history(stash_item.id)
        resolved_pack_id = pack.id

    resolved_ts = (
        observed_at
        or stash_item.updated_at
        or stash_item.created_at
        or datetime.now(UTC).strftime("%Y/%m/%d %H:%M:%S +0000")
    )

    history = self._load_pack_history(stash_item.id)

    history.observations.append(PackObservation(
        pack_id=resolved_pack_id,
        observed_at=resolved_ts,
    ))

    key = self._stash_history_key(stash_item.id)
    self.set_app_data(**{key: history.model_dump_json()})
    return history
```

**`delete_stash_pack_history(stash_id)` — cleanup (same as before, new name):**
```python
def delete_stash_pack_history(self, stash_id: int) -> dict[str, str]:
    """Delete the stored pack observation log for a stash item."""
    return self.delete_app_data([self._stash_history_key(stash_id)])
```

**Hook updates in `create_stash_item` and `update_stash_item`:**
```diff
- self.record_stash_snapshot(item)
+ self.record_pack_observation(item)
```

**Hook update in `delete_stash_item`:**
```diff
- self.delete_stash_history(stash_id)
+ self.delete_stash_pack_history(stash_id)
```

---

### Summary of Method Renames

| Old Name | New Name |
|---|---|
| `get_stash_history(stash_id)` | `get_stash_pack_history(stash_id)` |
| `get_batch_stash_history(stash_ids)` | `get_batch_stash_pack_history(stash_ids)` |
| `record_stash_snapshot(item, ts)` | `record_pack_observation(item, pack_id, observed_at)` |
| `delete_stash_history(stash_id)` | `delete_stash_pack_history(stash_id)` |

---

### Component 5: App Data storage format change

**Old format** (large, duplicating quantities):
```json
{
  "stash_id": 31516215,
  "entries": [
    {"timestamp": "2025/09/12 02:00:29 -0400", "skeins": 7.0, "total_grams": 700.0, "total_yards": 1379.0},
    {"timestamp": "2026/08/14 03:23:42 -0400", "skeins": 5.0, "total_grams": 500.0, "total_yards": 985.0}
  ]
}
```

**New format** (lean, references only):
```json
{
  "stash_id": 31516215,
  "observations": [
    {"pack_id": 134290871, "observed_at": "2025/09/12 02:00:29 -0400"},
    {"pack_id": 134290872, "observed_at": "2026/08/14 03:23:42 -0400"},
    {"pack_id": 135830458, "observed_at": "2026/08/14 03:15:00 -0400"}
  ]
}
```

Quantity data for any pack can be retrieved live from the API when needed.

---

## Verification Plan

### Manual Verification

Run the following in `dev.py` after implementation:

1. **Create a test stash item** → verify `stash_history_{id}` App Data key is written in new
   format (contains `observations`, not `entries`).
2. **Update the stash item's skeins** → verify a new `PackObservation` is appended (new `pack_id`,
   not a duplicate).
3. **Call `get_stash_pack_history(stash_id)`** → verify returned `StashPackHistory` has correct
   `observations` list with both pack IDs.
4. **Delete the stash item** → verify App Data key is cleaned up.

### Clean Up Existing Test Keys

```python
# One-time cleanup of old-format keys from prior testing
with RavelryClient() as client:
    client.delete_app_data(["stash_history_31516215"])
```
