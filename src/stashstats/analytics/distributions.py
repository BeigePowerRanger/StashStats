"""Stash inventory categorical distributions and aggregations."""

from collections import defaultdict
from pydantic import BaseModel, Field

from stashstats.models.stash import StashItem


class CategoryDistribution(BaseModel):
    """Aggregation metrics for a category dimension (yarn weight, fiber, brand, color)."""

    name: str
    """Category name or label."""

    count: int = 0
    """Number of stash items in this category."""

    total_yards: float = 0.0
    """Total length in yards."""

    total_meters: float = 0.0
    """Total length in meters."""

    total_grams: float = 0.0
    """Total weight in grams."""

    total_skeins: float = 0.0
    """Total skein count."""

    percentage_yards: float = 0.0
    """Share of overall stash yardage (0.0 - 100.0)."""

    percentage_count: float = 0.0
    """Share of overall stash item count (0.0 - 100.0)."""


class StashDistributionSummary(BaseModel):
    """Composite distributions breakdown for a user's stash."""

    weights: list[CategoryDistribution] = Field(default_factory=list)
    """Yarn weight distributions."""

    fibers: list[CategoryDistribution] = Field(default_factory=list)
    """Fiber composition distributions."""

    color_families: list[CategoryDistribution] = Field(default_factory=list)
    """Color family distributions."""

    brands: list[CategoryDistribution] = Field(default_factory=list)
    """Yarn manufacturer/brand distributions."""


class StashDistributionCalculator:
    """Calculates multidimensional distributions from active stash items."""

    @staticmethod
    def _aggregate_dimension(
        stash_items: list[StashItem],
        key_extractor: callable,
    ) -> list[CategoryDistribution]:
        """Generic aggregator helper over stash items for a given dimension extractor."""
        if not stash_items:
            return []

        grouped_count: dict[str, int] = defaultdict(int)
        grouped_yards: dict[str, float] = defaultdict(float)
        grouped_meters: dict[str, float] = defaultdict(float)
        grouped_grams: dict[str, float] = defaultdict(float)
        grouped_skeins: dict[str, float] = defaultdict(float)

        total_all_yards = 0.0
        total_all_count = len(stash_items)

        for item in stash_items:
            key = key_extractor(item) or "Uncategorized"
            yards = (
                (getattr(item, "yards_remaining", None) if getattr(item, "yards_remaining", None) is not None else item.total_yards)
                or 0.0
            )
            meters = (
                (getattr(item, "meters_remaining", None) if getattr(item, "meters_remaining", None) is not None else item.total_meters)
                or (yards * 0.9144 if yards else 0.0)
            )
            grams = (
                (getattr(item, "grams_remaining", None) if getattr(item, "grams_remaining", None) is not None else item.total_grams)
                or 0.0
            )
            skeins = (
                (getattr(item, "skeins_remaining", None) if getattr(item, "skeins_remaining", None) is not None else item.skeins)
                or 0.0
            )

            grouped_count[key] += 1
            grouped_yards[key] += yards
            grouped_meters[key] += meters
            grouped_grams[key] += grams
            grouped_skeins[key] += skeins
            total_all_yards += yards

        results: list[CategoryDistribution] = []
        for name in sorted(grouped_count.keys(), key=lambda k: grouped_yards[k], reverse=True):
            yards = grouped_yards[name]
            count = grouped_count[name]
            pct_yards = round((yards / total_all_yards * 100.0), 2) if total_all_yards > 0 else 0.0
            pct_count = round((count / total_all_count * 100.0), 2) if total_all_count > 0 else 0.0

            results.append(
                CategoryDistribution(
                    name=name,
                    count=count,
                    total_yards=round(yards, 2),
                    total_meters=round(grouped_meters[name], 2),
                    total_grams=round(grouped_grams[name], 2),
                    total_skeins=round(grouped_skeins[name], 2),
                    percentage_yards=pct_yards,
                    percentage_count=pct_count,
                )
            )

        return results

    @classmethod
    def aggregate_yarn_weights(cls, stash_items: list[StashItem]) -> list[CategoryDistribution]:
        """Aggregate stash by yarn weight classification."""
        def extract_weight(item: StashItem) -> str:
            if item.yarn_weight_name:
                return item.yarn_weight_name
            if item.yarn and item.yarn.yarn_weight and item.yarn.yarn_weight.name:
                return item.yarn.yarn_weight.name
            if item.personal_yarn_weight and item.personal_yarn_weight.name:
                return item.personal_yarn_weight.name
            return "Uncategorized"

        return cls._aggregate_dimension(stash_items, extract_weight)

    @classmethod
    def aggregate_color_families(cls, stash_items: list[StashItem]) -> list[CategoryDistribution]:
        """Aggregate stash by color family."""
        return cls._aggregate_dimension(
            stash_items,
            lambda item: item.color_family_name or "Uncategorized",
        )

    @classmethod
    def aggregate_brands(cls, stash_items: list[StashItem]) -> list[CategoryDistribution]:
        """Aggregate stash by yarn company/brand."""
        def extract_brand(item: StashItem) -> str:
            if item.yarn and item.yarn.yarn_company_name:
                return item.yarn.yarn_company_name
            if item.yarn and item.yarn.yarn_company and item.yarn.yarn_company.name:
                return item.yarn.yarn_company.name
            return "Unknown Brand"

        return cls._aggregate_dimension(stash_items, extract_brand)

    @classmethod
    def aggregate_fiber_categories(cls, stash_items: list[StashItem]) -> list[CategoryDistribution]:
        """Aggregate stash by fiber category or material."""
        def extract_fiber(item: StashItem) -> str:
            # 1. Check yarn fibers list if available on item or yarn model
            if item.yarn and getattr(item.yarn, "yarn_fibers", None):
                fibers = getattr(item.yarn, "yarn_fibers", [])
                if fibers:
                    top_fiber = max(fibers, key=lambda f: getattr(f, "percentage", 0) or 0)
                    ft = getattr(top_fiber, "fiber_type", None)
                    if ft and hasattr(ft, "name") and ft.name:
                        return str(ft.name).capitalize()
                    elif hasattr(top_fiber, "name") and top_fiber.name:
                        return str(top_fiber.name).capitalize()

            # 2. Check yarn name, item title, or tags for known fiber keywords
            tokens = " ".join(
                [
                    item.name or "",
                    (item.yarn.name if item.yarn else "") or "",
                    " ".join(item.tag_names or []),
                ]
            ).lower()
            for fiber_kw in ["merino", "alpaca", "silk", "cotton", "cashmere", "mohair", "wool", "acrylic", "linen", "nylon", "bamboo", "viscose"]:
                if fiber_kw in tokens:
                    return fiber_kw.capitalize()

            return "General / Mixed Fiber"

        return cls._aggregate_dimension(stash_items, extract_fiber)

    @classmethod
    def aggregate_all(cls, stash_items: list[StashItem]) -> StashDistributionSummary:
        """Calculate complete multidimensional distributions summary."""
        return StashDistributionSummary(
            weights=cls.aggregate_yarn_weights(stash_items),
            fibers=cls.aggregate_fiber_categories(stash_items),
            color_families=cls.aggregate_color_families(stash_items),
            brands=cls.aggregate_brands(stash_items),
        )
