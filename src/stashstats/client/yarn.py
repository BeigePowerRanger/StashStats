"""Yarn domain client mixin for Ravelry API."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Literal

from stashstats.cache import cached_yarn_details, cached_yarn_search
from stashstats.models import (
    FiberCategory,
    YarnDetailResponse,
    YarnSearchResponse,
    YarnWeightReference,
)
from stashstats.reference_db import get_reference_data, init_db, set_reference_data

if TYPE_CHECKING:
    from stashstats.base import BaseAPIClient

logger = logging.getLogger("stashstats.client.yarn")

YarnSort = Literal["best", "rating", "projects"]


class YarnClientMixin:
    """Mixin providing yarn search, yarn details, and yarn reference endpoints."""

    @cached_yarn_search
    def search_yarns(
        self: BaseAPIClient | Any,
        query: str = "",
        *,
        page: int = 1,
        page_size: int = 50,
        sort: YarnSort | str = "best",
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

    search_yarn = search_yarns

    @cached_yarn_details
    def get_yarn_details(
        self: BaseAPIClient | Any,
        yarn_id: int,
    ) -> YarnDetailResponse:
        """Fetch detailed information for a specific yarn.

        Args:
            yarn_id: Unique yarn database ID.

        Returns:
            YarnDetailResponse containing full yarn details.
        """
        data = self.get(f"/yarns/{yarn_id}.json", params={"include": "colorways"})
        return YarnDetailResponse.model_validate(data)

    get_yarn = get_yarn_details

    def get_yarn_weight_categories(
        self: BaseAPIClient | Any,
    ) -> list[YarnWeightReference]:
        """Fetch reference list of standard yarn weight classifications."""
        init_db()
        cached = get_reference_data("yarn_weights")
        if cached:
            return [YarnWeightReference.model_validate(w) for w in cached]

        data = self.get("/yarn_weights.json")
        yarn_weights = data.get("yarn_weights", [])
        set_reference_data("yarn_weights", yarn_weights)
        return [YarnWeightReference.model_validate(w) for w in yarn_weights]

    get_yarn_weights = get_yarn_weight_categories

    def get_fiber_categories(
        self: BaseAPIClient | Any,
    ) -> list[FiberCategory]:
        """Fetch reference list of top-level fiber categories."""
        init_db()
        cached = get_reference_data("fiber_categories")
        if cached:
            return [FiberCategory.model_validate(f) for f in cached]

        data = self.get("/fiber_categories.json")
        fiber_categories = data.get("fiber_categories", [])
        set_reference_data("fiber_categories", fiber_categories)
        return [FiberCategory.model_validate(f) for f in fiber_categories]
