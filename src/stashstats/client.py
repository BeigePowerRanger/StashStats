import json
import logging
from datetime import UTC, datetime
from typing import Any

from stashstats.base import BaseAPIClient
from stashstats.analytics import StashVelocityCalculator
from stashstats.models import (
    ColorFamily,
    CurrentUserResponse,
    FiberCategory,
    StashHistory,
    StashHistoryEntry,
    StashItem,
    StashListResponse,
    StashSearchResponse,
    StashVelocityReport,
    YarnDetailResponse,
    YarnSearchResponse,
    YarnWeightReference,
)
from stashstats.cache import cached_yarn_search, cached_yarn_details
from stashstats.reference_db import init_db, get_reference_data, set_reference_data

logger = logging.getLogger("stashstats.client")


class RavelryClient(BaseAPIClient):
    """High-level synchronous Ravelry API client with domain endpoints."""

    _cached_username: str | None = None

    def get_current_user(self) -> CurrentUserResponse:
        """Fetch the authenticated user's profile and cache username."""
        logger.debug("Fetching current authenticated user profile")
        data = self.get("/current_user.json")
        res = CurrentUserResponse.model_validate(data)
        self._cached_username = res.user.username
        logger.info(f"Authenticated as @{res.user.username}")
        return res

    @cached_yarn_search
    def search_yarns(
        self,
        query: str = "",
        *,
        page: int = 1,
        page_size: int = 50,
        sort: str = "best",
        personal_attributes: bool = False,
    ) -> YarnSearchResponse:
        """Search the Ravelry yarn database.

        Args:
            query: Fulltext search term.
            page: Result page index (1-indexed).
            page_size: Number of results per page (default 50).
            sort: Sort order ('best', 'rating', 'projects').
            personal_attributes: Whether to include personal attributes hash.

        Returns:
            YarnSearchResponse with paginator metadata and list of matching yarns.
        """
        params = {
            "query": query,
            "page": page,
            "page_size": page_size,
            "sort": sort,
            "personal_attributes": 1 if personal_attributes else None,
        }
        data = self.get("/yarns/search.json", params=params)
        return YarnSearchResponse.model_validate(data)

    @cached_yarn_details
    def get_yarn_details(self, yarn_id: int) -> YarnDetailResponse:
        """Fetch detailed information for a specific yarn.

        Args:
            yarn_id: Unique yarn database ID.

        Returns:
            YarnDetailResponse containing full yarn details.
        """
        data = self.get(f"/yarns/{yarn_id}.json", params={"include": "colorways"})
        return YarnDetailResponse.model_validate(data)

    def search_stash(
        self,
        query: str = "",
        *,
        page: int = 1,
        page_size: int = 50,
        sort: str = "best",
    ) -> StashSearchResponse:
        """Search public stash items across Ravelry.

        Args:
            query: Fulltext search term.
            page: Result page index (1-indexed).
            page_size: Number of results per page (default 50).
            sort: Sort order (e.g. 'best', 'rating', 'projects').

        Returns:
            StashSearchResponse with paginator metadata and list of matching stash items.
        """
        params = {
            "query": query,
            "page": page,
            "page_size": page_size,
            "sort": sort,
        }
        data = self.get("/stash/search.json", params=params)
        return StashSearchResponse.model_validate(data)

    def get_stash_list(
        self,
        username: str,
        *,
        page: int = 1,
        page_size: int = 50,
        sort: str = "created_",
        query: str | None = None,
        yarn_id: int | None = None,
        stash_status_id: int | None = None,
    ) -> StashListResponse:
        """Fetch a page of stash items for a specified user.

        Args:
            username: Ravelry username.
            page: Result page index (1-indexed).
            page_size: Number of items per page.
            sort: Sort order (e.g. 'created_', 'yarn_name', 'rating').
            query: Optional search filter within stash.
            yarn_id: Optional filter for a specific yarn.
            stash_status_id: Optional filter for stash status (e.g. 1 for 'In stash').

        Returns:
            StashListResponse with paginator metadata and list of stash items.
        """
        params = {
            "page": page,
            "page_size": page_size,
            "sort": sort,
            "query": query,
            "yarn_id": yarn_id,
            "stash_status_id": stash_status_id,
        }
        data = self.get(f"/people/{username}/stash/list.json", params=params)
        return StashListResponse.model_validate(data)

    def get_my_stash(
        self,
        *,
        username: str | None = None,
        page: int = 1,
        page_size: int = 50,
        sort: str = "created_",
        query: str | None = None,
        yarn_id: int | None = None,
        stash_status_id: int | None = None,
    ) -> StashListResponse:
        """Fetch a page of stash items for the currently authenticated user.

        Args:
            username: Optional explicit username override (otherwise cached from auth).
            page: Result page index (1-indexed).
            page_size: Number of items per page.
            sort: Sort order (e.g. 'created_', 'yarn_name', 'rating').
            query: Optional search filter within stash.
            yarn_id: Optional filter for a specific yarn.
            stash_status_id: Optional filter for stash status.

        Returns:
            StashListResponse for current authenticated user.
        """
        target_username = username or self._cached_username
        if not target_username:
            user_resp = self.get_current_user()
            target_username = user_resp.user.username

        return self.get_stash_list(
            username=target_username,
            page=page,
            page_size=page_size,
            sort=sort,
            query=query,
            yarn_id=yarn_id,
            stash_status_id=stash_status_id,
        )

    def get_all_my_stash(
        self,
        *,
        username: str | None = None,
        sort: str = "created_",
        query: str | None = None,
        yarn_id: int | None = None,
        stash_status_id: int | None = None,
    ) -> list[StashItem]:
        """Fetch all pages of stash items for the authenticated or specified user.

        Args:
            username: Optional username override.
            sort: Sort order.
            query: Optional search filter.
            yarn_id: Optional yarn ID filter.
            stash_status_id: Optional status filter.

        Returns:
            Complete list of all StashItem records across all pages.
        """
        all_items: list[StashItem] = []
        page = 1
        page_size = 100

        while True:
            resp = self.get_my_stash(
                username=username,
                page=page,
                page_size=page_size,
                sort=sort,
                query=query,
                yarn_id=yarn_id,
                stash_status_id=stash_status_id,
            )
            if not resp.stash:
                break
            all_items.extend(resp.stash)

            last_page = resp.paginator.last_page or resp.paginator.page_count
            if page >= last_page:
                break
            page += 1

        return all_items

    def get_stash_item(self, stash_id: int, username: str | None = None) -> StashItem:
        """Fetch details for a single stash entry.

        Args:
            stash_id: Unique stash item database ID.
            username: Optional username override (defaults to current user).

        Returns:
            Parsed StashItem record.
        """
        target_username = username or self._cached_username
        if not target_username:
            user_resp = self.get_current_user()
            target_username = user_resp.user.username

        data = self.get(f"/people/{target_username}/stash/{stash_id}.json")
        return StashItem.model_validate(data["stash"])

    def create_stash_item(
        self,
        yarn_id: int | None = None,
        *,
        yarn_name: str | None = None,
        yarn_company_name: str | None = None,
        colorway_name: str | None = None,
        dye_lot: str | None = None,
        skeins: float | None = None,
        total_grams: float | None = None,
        total_yards: float | None = None,
        location: str | None = None,
        notes: str | None = None,
        purchased_date: str | None = None,
        stash_status_id: int = 1,
        username: str | None = None,
    ) -> StashItem:
        """Add a yarn into the user's stash.

        Args:
            yarn_id: Optional Ravelry catalog yarn ID to link.
            yarn_name: Optional custom or manual yarn line name.
            yarn_company_name: Optional manufacturer or indie dyer name.
            colorway_name: Optional colorway name.
            dye_lot: Optional dye lot string.
            skeins: Number of skeins allocated.
            total_grams: Total weight in grams.
            total_yards: Total length in yards.
            location: Storage location description.
            notes: Personal stash notes.
            purchased_date: Purchase or addition date string.
            stash_status_id: 1 for active/in stash, 2 for used up, etc.
            username: Optional username override.

        Returns:
            Parsed StashItem record for the newly created stash entry.
        """
        target_username = username or self._cached_username
        if not target_username:
            user_resp = self.get_current_user()
            target_username = user_resp.user.username

        pack_data: dict[str, Any] = {}
        if colorway_name is not None:
            pack_data["colorway"] = colorway_name
        if dye_lot is not None:
            pack_data["dye_lot"] = dye_lot
        if skeins is not None:
            pack_data["skeins"] = skeins
        if total_grams is not None:
            pack_data["total_grams"] = total_grams
        if total_yards is not None:
            pack_data["total_yards"] = total_yards
        if yarn_name is not None:
            pack_data["yarn_name"] = yarn_name

        payload: dict[str, Any] = {
            "stash_status_id": stash_status_id,
        }
        if yarn_id is not None:
            payload["yarn_id"] = yarn_id
        if yarn_name is not None:
            payload["name"] = yarn_name
        if yarn_company_name is not None:
            payload["yarn_company_name"] = yarn_company_name
        if colorway_name is not None:
            payload["colorway_name"] = colorway_name
        if dye_lot is not None:
            payload["dye_lot"] = dye_lot
        if location is not None:
            payload["location"] = location
        if notes is not None:
            payload["notes"] = notes
        if pack_data:
            payload["pack"] = pack_data

        data = self.post(f"/people/{target_username}/stash/create.json", json=payload)
        stash_dict = dict(data.get("stash", {}))

        # Preserve custom name/brand on returned model if API returned untitled
        if yarn_name and stash_dict.get("name") in ("untitled", "", None):
            full_title = f"{yarn_company_name or ''} {yarn_name}".strip()
            stash_dict["name"] = full_title
        if colorway_name and not stash_dict.get("colorway_name"):
            stash_dict["colorway_name"] = colorway_name

        item = StashItem.model_validate(stash_dict)
        self.record_stash_snapshot(item)
        return item

    def update_stash_item(
        self,
        stash_id: int,
        *,
        location: str | None = None,
        colorway_name: str | None = None,
        dye_lot: str | None = None,
        stash_status_id: int | None = None,
        handspun: bool | None = None,
        notes: str | None = None,
        tag_list: str | None = None,
        skeins: float | None = None,
        total_grams: float | None = None,
        total_yards: float | None = None,
        pack_id: int | None = None,
        username: str | None = None,
    ) -> StashItem:
        """Update fields on an existing stash record.

        Args:
            stash_id: Database ID of the stash item to modify.
            location: Storage location description.
            colorway_name: Colorway name or number.
            dye_lot: Dye lot identifier.
            stash_status_id: Status integer (1=in stash, 2=used up, 3=will trade/sell, 4=gone/sold).
            handspun: Whether yarn is handspun.
            notes: Personal notes on the stash item.
            tag_list: Space-delimited list of tags.
            skeins: Number of skeins allocated.
            total_grams: Total weight in grams.
            total_yards: Total length in yards.
            pack_id: Associated pack ID to update.
            username: Optional username override.

        Returns:
            Updated StashItem record.
        """
        target_username = username or self._cached_username
        if not target_username:
            user_resp = self.get_current_user()
            target_username = user_resp.user.username

        payload: dict[str, Any] = {}
        if location is not None:
            payload["location"] = location
        if colorway_name is not None:
            payload["colorway_name"] = colorway_name
        if dye_lot is not None:
            payload["dye_lot"] = dye_lot
        if stash_status_id is not None:
            payload["stash_status_id"] = stash_status_id
        if handspun is not None:
            payload["handspun"] = handspun
        if notes is not None:
            payload["notes"] = notes
        if tag_list is not None:
            payload["tag_list"] = tag_list

        pack_data: dict[str, Any] = {}
        if pack_id is not None:
            pack_data["id"] = pack_id
        if colorway_name is not None:
            pack_data["colorway"] = colorway_name
        if dye_lot is not None:
            pack_data["dye_lot"] = dye_lot
        if skeins is not None:
            pack_data["skeins"] = skeins
        if total_grams is not None:
            pack_data["total_grams"] = total_grams
        if total_yards is not None:
            pack_data["total_yards"] = total_yards
        if pack_data:
            payload["pack"] = pack_data

        data = self.post(f"/people/{target_username}/stash/{stash_id}.json", json=payload)
        item = StashItem.model_validate(data["stash"])
        self.record_stash_snapshot(item)
        return item

    def delete_stash_item(self, stash_id: int, username: str | None = None) -> dict[str, Any]:
        """Delete a stash entry and clean up associated history.

        Args:
            stash_id: Unique stash item database ID to remove.
            username: Optional username override.

        Returns:
            API confirmation response.
        """
        target_username = username or self._cached_username
        if not target_username:
            user_resp = self.get_current_user()
            target_username = user_resp.user.username

        res = self.delete(f"/people/{target_username}/stash/{stash_id}.json")
        self.delete_stash_history(stash_id)
        return res

    def get_app_data(self, keys: list[str]) -> dict[str, str]:
        """Retrieve stored user key/value pairs from Ravelry app data storage.

        Args:
            keys: List of string keys to retrieve.

        Returns:
            Dictionary of stored key/value pairs.
        """
        data = self.get("/app/data/get.json", params={"keys": " ".join(keys)})
        return data.get("data", data)

    def set_app_data(self, data_dict: dict[str, str] | None = None, **key_values: str) -> dict[str, str]:
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

    def delete_app_data(self, keys: list[str]) -> dict[str, str]:
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

    def get_stash_history(self, stash_id: int, user_id: str | int | None = None) -> StashHistory:
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

    def get_batch_stash_history(
        self,
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
        self,
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

        history = self.get_stash_history(stash_item.id, user_id=user_id)
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

        key = self._stash_history_key(stash_item.id, user_id=user_id)
        self.set_app_data(**{key: history.model_dump_json()})
        return history

    def delete_stash_history(self, stash_id: int, user_id: str | int | None = None) -> dict[str, str]:
        """Delete stored quantity history for a stash item.

        Args:
            stash_id: Unique stash item database ID.
            user_id: Optional user identifier for namespaced history.

        Returns:
            Dictionary of deleted keys and previous values.
        """
        key = self._stash_history_key(stash_id, user_id=user_id)
        return self.delete_app_data([key])

    def get_color_families(self) -> list[ColorFamily]:
        """Fetch reference list of all Ravelry color families."""
        init_db()
        cached = get_reference_data("color_families")
        if cached:
            return [ColorFamily.model_validate(c) for c in cached]
            
        data = self.get("/color_families.json")
        color_families = data.get("color_families", [])
        set_reference_data("color_families", color_families)
        return [ColorFamily.model_validate(c) for c in color_families]

    def get_yarn_weights(self) -> list[YarnWeightReference]:
        """Fetch reference list of standard yarn weight classifications."""
        init_db()
        cached = get_reference_data("yarn_weights")
        if cached:
            return [YarnWeightReference.model_validate(w) for w in cached]
            
        data = self.get("/yarn_weights.json")
        yarn_weights = data.get("yarn_weights", [])
        set_reference_data("yarn_weights", yarn_weights)
        return [YarnWeightReference.model_validate(w) for w in yarn_weights]

    def get_fiber_categories(self) -> list[FiberCategory]:
        """Fetch reference list of top-level fiber categories."""
        init_db()
        cached = get_reference_data("fiber_categories")
        if cached:
            return [FiberCategory.model_validate(f) for f in cached]
            
        data = self.get("/fiber_categories.json")
        fiber_categories = data.get("fiber_categories", [])
        set_reference_data("fiber_categories", fiber_categories)
        return [FiberCategory.model_validate(f) for f in fiber_categories]

    def get_stash_velocity_report(
        self,
        username: str | None = None,
        user_id: str | int | None = None,
        as_of: datetime | None = None,
    ) -> StashVelocityReport:
        """Fetch complete user stash across all pages, batch-load quantity histories, and compute velocity report.

        Args:
            username: Optional username override (defaults to authenticated user).
            user_id: Optional user ID for namespaced history storage.
            as_of: Benchmark date for trailing velocity windows.

        Returns:
            Computed StashVelocityReport.
        """
        stash_items = self.get_all_my_stash(username=username)
        stash_ids = [item.id for item in stash_items]
        histories = self.get_batch_stash_history(stash_ids, user_id=user_id)
        return StashVelocityCalculator.generate_report(stash_items, histories, as_of=as_of)

