from stashstats.analytics.distributions import (
    CategoryDistribution,
    StashDistributionCalculator,
    StashDistributionSummary,
)
from stashstats.models.common import YarnCompany
from stashstats.models.stash import StashItem, StashYarn
from stashstats.models.yarn import FiberType, YarnFiber, YarnWeight


def sample_stash_items() -> list[StashItem]:
    return [
        StashItem(
            id=1,
            name="Malabrigo Rios",
            permalink="malabrigo-rios",
            colorway_name="Azul Profundo",
            color_family_name="Blue",
            yarn_weight_name="Worsted",
            skeins=3.0,
            total_yards=630.0,
            total_grams=300.0,
            yarn=StashYarn(
                id=101,
                name="Rios",
                yarn_company_name="Malabrigo",
                yarn_company=YarnCompany(id=10, name="Malabrigo"),
                yarn_weight=YarnWeight(id=4, name="Worsted"),
            ),
        ),
        StashItem(
            id=2,
            name="Malabrigo Sock",
            permalink="malabrigo-sock",
            colorway_name="Lettuce",
            color_family_name="Green",
            yarn_weight_name="Fingering",
            skeins=2.0,
            total_yards=880.0,
            total_grams=200.0,
            yarn=StashYarn(
                id=102,
                name="Sock",
                yarn_company_name="Malabrigo",
                yarn_company=YarnCompany(id=10, name="Malabrigo"),
                yarn_weight=YarnWeight(id=1, name="Fingering"),
            ),
        ),
        StashItem(
            id=3,
            name="Cascade 220",
            permalink="cascade-220",
            colorway_name="Navy",
            color_family_name="Blue",
            yarn_weight_name="Worsted",
            skeins=1.0,
            total_yards=220.0,
            total_grams=100.0,
            yarn=StashYarn(
                id=103,
                name="220",
                yarn_company_name="Cascade Yarns",
                yarn_company=YarnCompany(id=20, name="Cascade Yarns"),
                yarn_weight=YarnWeight(id=4, name="Worsted"),
            ),
        ),
    ]


class TestStashDistributionCalculator:
    def test_aggregate_yarn_weights(self):
        items = sample_stash_items()
        weights = StashDistributionCalculator.aggregate_yarn_weights(items)

        # Worsted: 2 items, 4 skeins, 850 yards
        # Fingering: 1 item, 2 skeins, 880 yards
        assert len(weights) == 2
        worsted = next(w for w in weights if w.name == "Worsted")
        assert worsted.count == 2
        assert worsted.total_skeins == 4.0
        assert worsted.total_yards == 850.0
        assert worsted.total_grams == 400.0

        fingering = next(w for w in weights if w.name == "Fingering")
        assert fingering.count == 1
        assert fingering.total_skeins == 2.0
        assert fingering.total_yards == 880.0
        assert fingering.total_grams == 200.0

        # Percentages sum close to 100
        total_pct = sum(w.percentage_yards for w in weights)
        assert abs(total_pct - 100.0) < 0.1

    def test_aggregate_color_families(self):
        items = sample_stash_items()
        colors = StashDistributionCalculator.aggregate_color_families(items)

        assert len(colors) == 2
        blue = next(c for c in colors if c.name == "Blue")
        assert blue.count == 2
        assert blue.total_yards == 850.0

        green = next(c for c in colors if c.name == "Green")
        assert green.count == 1
        assert green.total_yards == 880.0

    def test_aggregate_brands(self):
        items = sample_stash_items()
        brands = StashDistributionCalculator.aggregate_brands(items)

        assert len(brands) == 2
        malabrigo = next(b for b in brands if b.name == "Malabrigo")
        assert malabrigo.count == 2
        assert malabrigo.total_yards == 1510.0

        cascade = next(b for b in brands if b.name == "Cascade Yarns")
        assert cascade.count == 1
        assert cascade.total_yards == 220.0

    def test_aggregate_all(self):
        items = sample_stash_items()
        summary = StashDistributionCalculator.aggregate_all(items)

        assert isinstance(summary, StashDistributionSummary)
        assert len(summary.weights) == 2
        assert len(summary.color_families) == 2
        assert len(summary.brands) == 2

    def test_empty_stash(self):
        summary = StashDistributionCalculator.aggregate_all([])
        assert summary.weights == []
        assert summary.color_families == []
        assert summary.brands == []
