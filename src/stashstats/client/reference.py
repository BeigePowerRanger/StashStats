"""Reference data domain client mixin for Ravelry API."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from stashstats.models import ColorFamily, FiberCategory, YarnWeightReference
from stashstats.reference_db import get_reference_data, init_db, set_reference_data

if TYPE_CHECKING:
    from stashstats.base import BaseAPIClient

logger = logging.getLogger("stashstats.client.reference")


class ReferenceClientMixin:
    """Mixin providing reference data endpoints: color families, crafts, project statuses, etc."""

    def get_color_families(self: BaseAPIClient | Any) -> list[ColorFamily]:
        """Fetch reference list of all Ravelry color families."""
        init_db()
        cached = get_reference_data("color_families")
        if cached:
            return [ColorFamily.model_validate(c) for c in cached]

        data = self.get("/color_families.json")
        color_families = data.get("color_families", [])
        set_reference_data("color_families", color_families)
        return [ColorFamily.model_validate(c) for c in color_families]

    def get_crafts(self: BaseAPIClient | Any) -> list[dict[str, Any]]:
        """Fetch list of valid crafts for projects."""
        try:
            data = self.get("/projects/crafts.json")
        except Exception:
            data = self.post("/projects/crafts.json")
        return data.get("crafts", data if isinstance(data, list) else [])

    def get_project_statuses(self: BaseAPIClient | Any) -> list[dict[str, Any]]:
        """Fetch list of valid project statuses."""
        try:
            data = self.get("/projects/project_statuses.json")
        except Exception:
            data = self.post("/projects/project_statuses.json")
        return data.get("project_statuses", data if isinstance(data, list) else [])

    def get_yarn_weights(self: BaseAPIClient | Any) -> list[YarnWeightReference]:
        """Fetch reference list of standard yarn weight classifications."""
        init_db()
        cached = get_reference_data("yarn_weights")
        if cached:
            return [YarnWeightReference.model_validate(w) for w in cached]

        data = self.get("/yarn_weights.json")
        yarn_weights = data.get("yarn_weights", [])
        set_reference_data("yarn_weights", yarn_weights)
        return [YarnWeightReference.model_validate(w) for w in yarn_weights]

    def get_fiber_categories(self: BaseAPIClient | Any) -> list[FiberCategory]:
        """Fetch reference list of top-level fiber categories."""
        init_db()
        cached = get_reference_data("fiber_categories")
        if cached:
            return [FiberCategory.model_validate(f) for f in cached]

        data = self.get("/fiber_categories.json")
        fiber_categories = data.get("fiber_categories", [])
        set_reference_data("fiber_categories", fiber_categories)
        return [FiberCategory.model_validate(f) for f in fiber_categories]
