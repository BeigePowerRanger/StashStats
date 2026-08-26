"""High-level synchronous Ravelry API client combining domain mixins."""

from __future__ import annotations

import logging
from typing import Any

from stashstats.base import BaseAPIClient
from stashstats.client.app_data import AppDataClientMixin
from stashstats.client.projects import ProjectClientMixin
from stashstats.client.reference import ReferenceClientMixin
from stashstats.client.stash import StashClientMixin
from stashstats.client.yarn import YarnClientMixin
from stashstats.models import CurrentUserResponse

logger = logging.getLogger("stashstats.client")


class RavelryClient(
    BaseAPIClient,
    YarnClientMixin,
    StashClientMixin,
    ProjectClientMixin,
    AppDataClientMixin,
    ReferenceClientMixin,
):
    """High-level synchronous Ravelry API client with domain endpoints."""

    _cached_username: str | None = None

    @property
    def username(self) -> str:
        """Get the authenticated username, fetching from API if not cached."""
        if not self._cached_username:
            self.get_current_user()
        return self._cached_username or ""

    def get_current_user(self) -> CurrentUserResponse:
        """Fetch the authenticated user's profile and cache username."""
        logger.debug("Fetching current authenticated user profile")
        data = self.get("/current_user.json")
        res = CurrentUserResponse.model_validate(data)
        self._cached_username = res.user.username
        logger.info(f"Authenticated as @{res.user.username}")
        return res

    # Extra pattern, favorite, queue helpers for scripts/testing compatibility
    def search_patterns(self, query: str = "", **kwargs: Any) -> Any:
        """Search patterns catalog."""
        params = {"query": query, **kwargs}
        return self.get("/patterns/search.json", params=params)

    def get_pattern(self, pattern_id: int) -> Any:
        """Get pattern details."""
        return self.get(f"/patterns/{pattern_id}.json")

    def get_favorites(self, username: str | None = None, **kwargs: Any) -> Any:
        """List user favorites."""
        target = username or self.username
        return self.get(f"/people/{target}/favorites/list.json", params=kwargs)

    def add_favorite(self, favorite_data: dict[str, Any], username: str | None = None) -> Any:
        """Add an item to favorites."""
        target = username or self.username
        return self.post(f"/people/{target}/favorites/create.json", json=favorite_data)

    def remove_favorite(self, favorite_id: int, username: str | None = None) -> Any:
        """Remove an item from favorites."""
        target = username or self.username
        return self.delete(f"/people/{target}/favorites/{favorite_id}.json")

    def get_queue(self, username: str | None = None, **kwargs: Any) -> Any:
        """List user queued projects."""
        target = username or self.username
        return self.get(f"/people/{target}/queue/list.json", params=kwargs)

    def add_to_queue(self, queue_data: dict[str, Any], username: str | None = None) -> Any:
        """Add an item to queue."""
        target = username or self.username
        return self.post(f"/people/{target}/queue/create.json", json=queue_data)

    def remove_from_queue(self, queue_id: int, username: str | None = None) -> Any:
        """Remove an item from queue."""
        target = username or self.username
        return self.delete(f"/people/{target}/queue/{queue_id}.json")


Client = RavelryClient
