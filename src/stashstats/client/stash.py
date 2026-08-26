"""Stash domain client mixin for Ravelry API."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal

from stashstats.analytics import StashVelocityCalculator
from stashstats.models import (
    Pack,
    StashItem,
    StashListResponse,
    StashSearchResponse,
    StashVelocityReport,
)

if TYPE_CHECKING:
    from stashstats.base import BaseAPIClient

logger = logging.getLogger("stashstats.client.stash")

StashSort = Literal["best", "rating", "projects", "created_", "yarn_name"]


class StashClientMixin:
    """Mixin providing stash inventory management, searches, and pack operations."""

    def search_stash(
        self: BaseAPIClient | Any,
        query: str = "",
        *,
        page: int = 1,
        page_size: int = 50,
        sort: StashSort | str = "best",
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
        self: BaseAPIClient | Any,
        username: str,
        *,
        page: int = 1,
        page_size: int = 50,
        sort: StashSort | str = "created_",
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

    def get_stash_items(
        self: BaseAPIClient | Any,
        username: str | None = None,
        *,
        page: int = 1,
        page_size: int = 50,
        sort: StashSort | str = "created_",
        query: str | None = None,
        yarn_id: int | None = None,
        stash_status_id: int | None = None,
    ) -> StashListResponse:
        """Fetch a page of stash items for the currently authenticated or specified user."""
        target_username = username or getattr(self, "username", None) or getattr(self, "_cached_username", None)
        if not target_username and hasattr(self, "get_current_user"):
            user_resp = self.get_current_user()
            target_username = user_resp.user.username

        return self.get_stash_list(
            username=target_username or "",
            page=page,
            page_size=page_size,
            sort=sort,
            query=query,
            yarn_id=yarn_id,
            stash_status_id=stash_status_id,
        )

    get_my_stash = get_stash_items

    def get_all_my_stash(
        self: BaseAPIClient | Any,
        *,
        username: str | None = None,
        sort: StashSort | str = "created_",
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

    def get_stash_item(
        self: BaseAPIClient | Any,
        stash_id: int,
        username: str | None = None,
    ) -> StashItem:
        """Fetch details for a single stash entry.

        Args:
            stash_id: Unique stash item database ID.
            username: Optional username override (defaults to current user).

        Returns:
            Parsed StashItem record.
        """
        target_username = username or getattr(self, "username", None) or getattr(self, "_cached_username", None)
        if not target_username and hasattr(self, "get_current_user"):
            user_resp = self.get_current_user()
            target_username = user_resp.user.username

        data = self.get(f"/people/{target_username}/stash/{stash_id}.json")
        return StashItem.model_validate(data["stash"])

    def create_stash_item(
        self: BaseAPIClient | Any,
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
        target_username = username or getattr(self, "username", None) or getattr(self, "_cached_username", None)
        if not target_username and hasattr(self, "get_current_user"):
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
        if hasattr(self, "record_stash_snapshot"):
            self.record_stash_snapshot(item)
        return item

    def update_stash_item(
        self: BaseAPIClient | Any,
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
        target_username = username or getattr(self, "username", None) or getattr(self, "_cached_username", None)
        if not target_username and hasattr(self, "get_current_user"):
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
        if hasattr(self, "record_stash_snapshot"):
            self.record_stash_snapshot(item)
        return item

    def delete_stash_item(
        self: BaseAPIClient | Any,
        stash_id: int,
        username: str | None = None,
    ) -> dict[str, Any]:
        """Delete a stash entry and clean up associated history.

        Args:
            stash_id: Unique stash item database ID to remove.
            username: Optional username override.

        Returns:
            API confirmation response.
        """
        target_username = username or getattr(self, "username", None) or getattr(self, "_cached_username", None)
        if not target_username and hasattr(self, "get_current_user"):
            user_resp = self.get_current_user()
            target_username = user_resp.user.username

        res = self.delete(f"/people/{target_username}/stash/{stash_id}.json")
        if hasattr(self, "delete_stash_history"):
            self.delete_stash_history(stash_id)
        return res

    def create_stash_pack(
        self: BaseAPIClient | Any,
        stash_id: int,
        pack_data: dict[str, Any] | Pack | None = None,
        **kwargs: Any,
    ) -> Pack | dict[str, Any]:
        """Create a new pack associated with a stash entry."""
        payload = dict(pack_data.model_dump() if hasattr(pack_data, "model_dump") else (pack_data or {}))
        payload.update(kwargs)
        data = self.post("/packs/create.json", json={"pack": payload, "stash_id": stash_id})
        if isinstance(data, dict) and "pack" in data:
            return Pack.model_validate(data["pack"])
        return data

    def update_stash_pack(
        self: BaseAPIClient | Any,
        pack_id: int,
        pack_data: dict[str, Any] | Pack | None = None,
        **kwargs: Any,
    ) -> Pack | dict[str, Any]:
        """Update an existing pack record."""
        payload = dict(pack_data.model_dump() if hasattr(pack_data, "model_dump") else (pack_data or {}))
        payload.update(kwargs)
        data = self.put(f"/packs/{pack_id}.json", json={"pack": payload})
        if isinstance(data, dict) and "pack" in data:
            return Pack.model_validate(data["pack"])
        return data

    def delete_stash_pack(
        self: BaseAPIClient | Any,
        pack_id: int,
    ) -> dict[str, Any]:
        """Delete a pack record."""
        return self.delete(f"/packs/{pack_id}.json")

    def create_stash_photo(
        self: BaseAPIClient | Any,
        stash_id: int,
        *,
        image_id: int | None = None,
        source_url: str | None = None,
        username: str | None = None,
    ) -> dict[str, Any]:
        """Attach a photo to a stash entry using uploaded image ID or source URL."""
        target_username = username or getattr(self, "username", None) or getattr(self, "_cached_username", None)
        if not target_username and hasattr(self, "get_current_user"):
            user_resp = self.get_current_user()
            target_username = user_resp.user.username

        payload: dict[str, Any] = {}
        if image_id is not None:
            payload["image_id"] = image_id
        if source_url is not None:
            payload["source_url"] = source_url

        return self.post(f"/people/{target_username}/stash/{stash_id}/create_photo.json", json=payload)

    def get_stash_velocity_report(
        self: BaseAPIClient | Any,
        username: str | None = None,
        user_id: str | int | None = None,
        as_of: datetime | None = None,
    ) -> StashVelocityReport:
        """Fetch complete user stash across all pages, batch-load quantity histories, and compute velocity report."""
        stash_items = self.get_all_my_stash(username=username)
        stash_ids = [item.id for item in stash_items]
        histories = self.get_batch_stash_history(stash_ids, user_id=user_id)
        return StashVelocityCalculator.generate_report(stash_items, histories, as_of=as_of)

    # Script/helper aliases
    def create_stash(self: BaseAPIClient | Any, username_or_yarn_id: Any = None, data_or_kwargs: Any = None, **kwargs: Any) -> Any:
        if isinstance(username_or_yarn_id, str) and isinstance(data_or_kwargs, dict):
            return self.post(f"/people/{username_or_yarn_id}/stash/create.json", json=data_or_kwargs)
        if isinstance(username_or_yarn_id, int):
            return self.create_stash_item(yarn_id=username_or_yarn_id, **kwargs)
        return self.create_stash_item(**kwargs)

    def update_stash(self: BaseAPIClient | Any, username_or_stash_id: Any = None, stash_id_or_data: Any = None, data_or_none: Any = None, **kwargs: Any) -> Any:
        if isinstance(username_or_stash_id, str) and isinstance(stash_id_or_data, int) and isinstance(data_or_none, dict):
            return self.post(f"/people/{username_or_stash_id}/stash/{stash_id_or_data}.json", json=data_or_none)
        if isinstance(username_or_stash_id, int):
            return self.update_stash_item(username_or_stash_id, **kwargs)
        return self.update_stash_item(stash_id_or_data, **kwargs)

    def delete_stash(self: BaseAPIClient | Any, username_or_stash_id: Any = None, stash_id_or_none: Any = None) -> Any:
        if isinstance(username_or_stash_id, str) and isinstance(stash_id_or_none, int):
            return self.delete_stash_item(stash_id_or_none, username=username_or_stash_id)
        return self.delete_stash_item(username_or_stash_id)
