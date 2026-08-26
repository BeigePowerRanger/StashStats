"""App data domain client mixin for Ravelry API."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from stashstats.models import StashHistory, StashHistoryEntry, StashItem

if TYPE_CHECKING:
    from stashstats.base import BaseAPIClient

logger = logging.getLogger("stashstats.client.app_data")


class AppDataClientMixin:
    """Mixin providing Ravelry app data storage, stash history snapshots, and retrieval."""

    def get_app_data(self: BaseAPIClient | Any, keys: list[str]) -> dict[str, str]:
        """Retrieve stored user key/value pairs from Ravelry app data storage.

        Args:
            keys: List of string keys to retrieve.

        Returns:
            Dictionary of stored key/value pairs.
        """
        data = self.get("/app/data/get.json", params={"keys": " ".join(keys)})
        return data.get("data", data)

    def set_app_data(
        self: BaseAPIClient | Any,
        data_dict: dict[str, str] | None = None,
        **key_values: str,
    ) -> dict[str, str]:
        """Store user and application-specific key/value data.

        Args:
            data_dict: Optional dictionary of key/value pairs.
            **key_values: Key/value pairs to set in app storage.

        Returns:
            Dictionary of updated key/value pairs.
        """
        params = dict(data_dict or {})
        params.update(key_values)
        data = self.post("/app/data/set.json", params=params)
        return data.get("data", data)

    def delete_app_data(self: BaseAPIClient | Any, keys: list[str]) -> dict[str, str]:
        """Delete stored key/value entries from Ravelry app data storage.

        Args:
            keys: List of string keys to delete.

        Returns:
            Dictionary containing previous contents of deleted keys.
        """
        data = self.post("/app/data/delete.json", params={"keys": " ".join(keys)})
        return data.get("data", data)

    def _stash_history_key(self, stash_id: int, user_id: str | int | None = None) -> str:
        """Generate the storage key for a stash item's history.

        Args:
            stash_id: Unique stash item database ID.
            user_id: Optional user ID or username for multi-user namespacing.

        Returns:
            Formatted app data storage key.
        """
        if user_id:
            return f"user_{user_id}_stash_history_{stash_id}"
        return f"stash_history_{stash_id}"

    def get_stash_history(
        self: BaseAPIClient | Any,
        stash_id: int,
        user_id: str | int | None = None,
    ) -> StashHistory:
        """Retrieve quantity history timeline for a stash item.

        Args:
            stash_id: Unique stash item database ID.
            user_id: Optional user identifier for namespaced history.

        Returns:
            Parsed StashHistory object with chronological snapshots.
        """
        key = self._stash_history_key(stash_id, user_id=user_id)
        app_data = self.get_app_data([key])
        raw_val = app_data.get(key)
        if not raw_val:
            return StashHistory(stash_id=stash_id, entries=[])

        if isinstance(raw_val, str):
            try:
                parsed = json.loads(raw_val)
            except json.JSONDecodeError:
                return StashHistory(stash_id=stash_id, entries=[])
        else:
            parsed = raw_val

        if isinstance(parsed, dict):
            return StashHistory.model_validate(parsed)
        elif isinstance(parsed, list):
            return StashHistory(
                stash_id=stash_id,
                entries=[StashHistoryEntry.model_validate(e) for e in parsed],
            )
        return StashHistory(stash_id=stash_id, entries=[])

    def save_stash_history(
        self: BaseAPIClient | Any,
        history: StashHistory,
        user_id: str | int | None = None,
    ) -> dict[str, str]:
        """Save a StashHistory object into app data storage.

        Args:
            history: StashHistory instance to serialize and store.
            user_id: Optional user identifier for namespaced storage.

        Returns:
            Updated key/value pairs dictionary.
        """
        key = self._stash_history_key(history.stash_id, user_id=user_id)
        return self.set_app_data(**{key: history.model_dump_json()})

    def append_stash_history_entry(
        self: BaseAPIClient | Any,
        stash_id: int,
        entry: StashHistoryEntry,
        user_id: str | int | None = None,
    ) -> StashHistory:
        """Append an entry to a stash item's history timeline with deduplication.

        Args:
            stash_id: Stash item ID.
            entry: New StashHistoryEntry to append.
            user_id: Optional user identifier.

        Returns:
            Updated StashHistory instance.
        """
        history = self.get_stash_history(stash_id, user_id=user_id)
        if history.entries:
            latest = history.entries[-1]
            if (
                latest.skeins,
                latest.total_grams,
                latest.total_yards,
            ) == (
                entry.skeins,
                entry.total_grams,
                entry.total_yards,
            ):
                return history

        history.entries.append(entry)
        self.save_stash_history(history, user_id=user_id)
        return history

    def get_batch_stash_history(
        self: BaseAPIClient | Any,
        stash_ids: list[int],
        user_id: str | int | None = None,
    ) -> dict[int, StashHistory]:
        """Retrieve quantity histories for multiple stash items in a single request.

        Args:
            stash_ids: List of stash item IDs to look up.
            user_id: Optional user identifier for namespaced history.

        Returns:
            Dictionary mapping stash IDs to their respective StashHistory objects.
        """
        if not stash_ids:
            return {}

        keys = [self._stash_history_key(sid, user_id=user_id) for sid in stash_ids]
        app_data = self.get_app_data(keys)

        result: dict[int, StashHistory] = {}
        for sid in stash_ids:
            key = self._stash_history_key(sid, user_id=user_id)
            raw_val = app_data.get(key)
            if not raw_val:
                result[sid] = StashHistory(stash_id=sid, entries=[])
                continue

            if isinstance(raw_val, str):
                try:
                    parsed = json.loads(raw_val)
                except json.JSONDecodeError:
                    result[sid] = StashHistory(stash_id=sid, entries=[])
                    continue
            else:
                parsed = raw_val

            if isinstance(parsed, dict):
                result[sid] = StashHistory.model_validate(parsed)
            elif isinstance(parsed, list):
                result[sid] = StashHistory(
                    stash_id=sid,
                    entries=[StashHistoryEntry.model_validate(e) for e in parsed],
                )
            else:
                result[sid] = StashHistory(stash_id=sid, entries=[])

        return result

    def record_stash_snapshot(
        self: BaseAPIClient | Any,
        stash_item: StashItem,
        timestamp: str | None = None,
        pack_id: int | None = None,
        delta_skeins: float | None = None,
        notes: str | None = None,
        user_id: str | int | None = None,
    ) -> StashHistory:
        """Record a quantity snapshot entry for a stash item in app data.

        Args:
            stash_item: The StashItem instance to snapshot.
            timestamp: Optional timestamp string override (defaults to item update time).
            pack_id: Optional pack ID.
            delta_skeins: Optional quantity delta.
            notes: Optional note.
            user_id: Optional user identifier for namespaced history.

        Returns:
            Updated StashHistory object.
        """
        pack = stash_item.primary_pack or (stash_item.packs[0] if stash_item.packs else None)
        resolved_pack_id = pack_id or (pack.id if pack else None)
        skeins = float(pack.skeins) if pack and pack.skeins is not None else 0.0
        total_grams = (
            float(pack.total_grams) if pack and pack.total_grams is not None else 0.0
        )
        total_yards = (
            float(pack.total_yards) if pack and pack.total_yards is not None else 0.0
        )

        ts = (
            timestamp
            or stash_item.updated_at
            or stash_item.created_at
            or datetime.now(UTC).strftime("%Y/%m/%d %H:%M:%S +0000")
        )

        entry = StashHistoryEntry(
            timestamp=ts,
            skeins=skeins,
            total_grams=total_grams,
            total_yards=total_yards,
            pack_id=resolved_pack_id,
            delta_skeins=delta_skeins,
            notes=notes,
        )

        return self.append_stash_history_entry(stash_item.id, entry, user_id=user_id)

    def delete_stash_history(
        self: BaseAPIClient | Any,
        stash_id: int,
        user_id: str | int | None = None,
    ) -> dict[str, str]:
        """Delete stored quantity history for a stash item.

        Args:
            stash_id: Unique stash item database ID.
            user_id: Optional user identifier for namespaced history.

        Returns:
            Dictionary of deleted keys and previous values.
        """
        key = self._stash_history_key(stash_id, user_id=user_id)
        return self.delete_app_data([key])
