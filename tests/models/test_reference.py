import pytest
from pydantic import ValidationError

from stashstats.models.reference import (
    ColorFamiliesResponse,
    ColorFamily,
    FiberCategoriesResponse,
    FiberCategory,
    YarnWeightReference,
    YarnWeightsResponse,
)


class TestColorFamily:
    def test_valid_color_family(self):
        data = {
            "id": 1,
            "name": "Red",
            "permalink": "red",
            "spectrum_order": 1,
        }
        cf = ColorFamily.model_validate(data)
        assert cf.id == 1
        assert cf.name == "Red"
        assert cf.permalink == "red"
        assert cf.spectrum_order == 1

    def test_color_family_optional_spectrum_order(self):
        data = {
            "id": 15,
            "name": "Natural/Undyed",
            "permalink": "natural-undyed",
        }
        cf = ColorFamily.model_validate(data)
        assert cf.id == 15
        assert cf.spectrum_order is None

    def test_color_family_missing_required_field(self):
        with pytest.raises(ValidationError):
            ColorFamily.model_validate({"name": "Red", "permalink": "red"})

    def test_color_families_response(self):
        data = {
            "color_families": [
                {"id": 1, "name": "Red", "permalink": "red", "spectrum_order": 1},
                {"id": 2, "name": "Orange", "permalink": "orange", "spectrum_order": 2},
            ]
        }
        resp = ColorFamiliesResponse.model_validate(data)
        assert len(resp.color_families) == 2
        assert resp.color_families[0].name == "Red"
        assert resp.color_families[1].name == "Orange"


class TestYarnWeightReference:
    def test_valid_yarn_weight_reference(self):
        data = {
            "id": 4,
            "name": "Worsted",
            "ply": "10",
            "wpi": "9-11",
            "min_gauge": 18.0,
            "max_gauge": 22.0,
            "crochet_gauge": "11-14 sc",
        }
        ywr = YarnWeightReference.model_validate(data)
        assert ywr.id == 4
        assert ywr.name == "Worsted"
        assert ywr.ply == "10"
        assert ywr.wpi == "9-11"
        assert ywr.min_gauge == 18.0
        assert ywr.max_gauge == 22.0
        assert ywr.crochet_gauge == "11-14 sc"

    def test_yarn_weight_reference_optionals(self):
        data = {
            "id": 1,
            "name": "Cobweb",
        }
        ywr = YarnWeightReference.model_validate(data)
        assert ywr.id == 1
        assert ywr.name == "Cobweb"
        assert ywr.ply is None
        assert ywr.min_gauge is None

    def test_yarn_weights_response(self):
        data = {
            "yarn_weights": [
                {"id": 1, "name": "Lace"},
                {"id": 2, "name": "Fingering"},
            ]
        }
        resp = YarnWeightsResponse.model_validate(data)
        assert len(resp.yarn_weights) == 2
        assert resp.yarn_weights[0].name == "Lace"


class TestFiberCategory:
    def test_valid_fiber_category(self):
        data = {
            "id": 1,
            "name": "Animal fiber",
            "permalink": "animal-fiber",
        }
        fc = FiberCategory.model_validate(data)
        assert fc.id == 1
        assert fc.name == "Animal fiber"
        assert fc.permalink == "animal-fiber"

    def test_fiber_categories_response(self):
        data = {
            "fiber_categories": [
                {"id": 1, "name": "Animal fiber", "permalink": "animal-fiber"},
                {"id": 2, "name": "Plant fiber", "permalink": "plant-fiber"},
            ]
        }
        resp = FiberCategoriesResponse.model_validate(data)
        assert len(resp.fiber_categories) == 2
        assert resp.fiber_categories[1].name == "Plant fiber"
