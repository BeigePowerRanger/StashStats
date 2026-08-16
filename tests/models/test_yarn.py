
import pytest
from pydantic import ValidationError

from stashstats.models.yarn import (
    Colorway,
    FiberType,
    Yarn,
    YarnDetailResponse,
    YarnFiber,
    YarnSearchResponse,
    YarnSearchResult,
    YarnWeight,
)


class TestFiberType:
    def test_fiber_type_defaults(self):
        ft = FiberType.model_validate({"id": 1, "name": "Merino"})
        assert ft.id == 1
        assert ft.name == "Merino"
        assert ft.animal_fiber is False
        assert ft.synthetic is False
        assert ft.vegetable is False

    def test_fiber_type_flags(self):
        ft = FiberType.model_validate(
            {"id": 2, "name": "Alpaca", "animal_fiber": True, "synthetic": False, "vegetable": False}
        )
        assert ft.animal_fiber is True

    def test_fiber_type_null_flags_coerce_false(self):
        ft = FiberType.model_validate(
            {"id": 3, "name": "Bamboo", "animal_fiber": None, "synthetic": None, "vegetable": None}
        )
        assert ft.animal_fiber is False
        assert ft.synthetic is False
        assert ft.vegetable is False

    def test_fiber_type_empty_name_fails(self):
        with pytest.raises(ValidationError):
            FiberType.model_validate({"id": 1, "name": "  "})


class TestYarnFiber:
    def test_valid_yarn_fiber(self):
        data = {
            "id": 10,
            "percentage": 100,
            "fiber_type": {"id": 1, "name": "Wool", "animal_fiber": True},
        }
        yf = YarnFiber.model_validate(data)
        assert yf.id == 10
        assert yf.percentage == 100
        assert yf.fiber_type.name == "Wool"

    def test_percentage_conversion(self):
        data = {
            "id": 11,
            "percentage": "75",
            "fiber_type": {"id": 2, "name": "Cotton"},
        }
        yf = YarnFiber.model_validate(data)
        assert yf.percentage == 75

        data_float = {
            "id": 12,
            "percentage": 49.6,
            "fiber_type": {"id": 3, "name": "Nylon"},
        }
        yf_float = YarnFiber.model_validate(data_float)
        assert yf_float.percentage == 50

    @pytest.mark.parametrize("invalid_pct", [-1, 101, 150, -50])
    def test_percentage_out_of_bounds_fails(self, invalid_pct):
        with pytest.raises(ValidationError):
            YarnFiber.model_validate(
                {
                    "id": 10,
                    "percentage": invalid_pct,
                    "fiber_type": {"id": 1, "name": "Wool"},
                }
            )

    def test_percentage_none_fails(self):
        with pytest.raises(ValidationError):
            YarnFiber.model_validate(
                {
                    "id": 10,
                    "percentage": None,
                    "fiber_type": {"id": 1, "name": "Wool"},
                }
            )


class TestColorway:
    def test_colorway_with_family(self):
        cw = Colorway.model_validate({"id": 101, "name": "Frank Ochre", "color_family_id": 3})
        assert cw.id == 101
        assert cw.name == "Frank Ochre"
        assert cw.color_family_id == 3

    def test_colorway_without_family(self):
        cw = Colorway.model_validate({"id": 102, "name": "Custom Dye"})
        assert cw.color_family_id is None

    def test_colorway_negative_family_id_fails(self):
        with pytest.raises(ValidationError):
            Colorway.model_validate({"id": 103, "name": "Invalid Family", "color_family_id": -1})

    def test_colorway_empty_name_fails(self):
        with pytest.raises(ValidationError):
            Colorway.model_validate({"id": 104, "name": ""})


class TestYarnWeight:
    def test_yarn_weight(self):
        data = {
            "id": 5,
            "name": "Worsted",
            "ply": "10",
            "wpi": "9",
            "min_gauge": 18.0,
            "max_gauge": 20.0,
            "knit_gauge": "18-20 sts = 4 inches",
        }
        yw = YarnWeight.model_validate(data)
        assert yw.id == 5
        assert yw.name == "Worsted"
        assert yw.min_gauge == 18.0
        assert yw.max_gauge == 20.0

    def test_yarn_weight_gauge_range_validation(self):
        with pytest.raises(ValidationError, match="min_gauge .* cannot be greater than max_gauge"):
            YarnWeight.model_validate(
                {
                    "id": 5,
                    "name": "Worsted",
                    "min_gauge": 22.0,
                    "max_gauge": 18.0,
                }
            )

    def test_yarn_weight_negative_gauge_fails(self):
        with pytest.raises(ValidationError):
            YarnWeight.model_validate({"id": 5, "name": "Worsted", "min_gauge": -1.0})

    def test_yarn_weight_numeric_wpi_and_ply_normalized(self):
        yw = YarnWeight.model_validate({"id": 5, "name": "Worsted", "ply": 10, "wpi": 9})
        assert yw.ply == "10"
        assert yw.wpi == "9"

    def test_yarn_weight_empty_wpi_and_ply_normalized_to_none(self):
        yw = YarnWeight.model_validate({"id": 5, "name": "Worsted", "ply": "  ", "wpi": ""})
        assert yw.ply is None
        assert yw.wpi is None

    def test_yarn_weight_empty_name_fails(self):
        with pytest.raises(ValidationError):
            YarnWeight.model_validate({"id": 5, "name": "   "})


class TestYarn:
    def test_full_yarn_deserialization(self):
        data = {
            "id": 2420,
            "name": "Rios",
            "permalink": "malabrigo-yarn-rios",
            "yarn_company_name": "Malabrigo Yarn",
            "yarn_company": {
                "id": 47,
                "name": "Malabrigo Yarn",
                "permalink": "malabrigo-yarn",
                "url": "http://www.malabrigoyarn.com",
            },
            "yarn_weight": {
                "id": 5,
                "name": "Worsted",
                "ply": "4",
                "wpi": "10",
            },
            "grams": 100.0,
            "yardage": 210.0,
            "rating_average": 4.78,
            "rating_count": 8940,
            "discontinued": False,
            "machine_washable": True,
            "texture": "plied",
            "gauge_description": "18.0 to 22.0 sts = 4 inches",
            "yarn_fibers": [
                {
                    "id": 1,
                    "percentage": 100,
                    "fiber_type": {
                        "id": 1,
                        "name": "Merino",
                        "animal_fiber": True,
                    },
                }
            ],
            "photos": [
                {
                    "id": 12345,
                    "square_url": "https://images.ravelry.com/photo/sq.jpg",
                    "medium_url": "https://images.ravelry.com/photo/med.jpg",
                }
            ],
        }
        yarn = Yarn.model_validate(data)
        assert yarn.id == 2420
        assert yarn.name == "Rios"
        assert yarn.yarn_company is not None
        assert yarn.yarn_company.name == "Malabrigo Yarn"
        assert yarn.yarn_weight is not None
        assert yarn.yarn_weight.name == "Worsted"
        assert len(yarn.yarn_fibers) == 1
        assert yarn.yarn_fibers[0].percentage == 100
        assert len(yarn.photos) == 1
        assert yarn.machine_washable is True

    def test_minimal_yarn(self):
        data = {
            "id": 100,
            "name": "Mystery Yarn",
            "permalink": "mystery-yarn",
        }
        yarn = Yarn.model_validate(data)
        assert yarn.id == 100
        assert yarn.name == "Mystery Yarn"
        assert yarn.grams is None
        assert yarn.yarn_fibers == []
        assert yarn.photos == []
        assert yarn.discontinued is False

    def test_yarn_null_collections_and_flags(self):
        data = {
            "id": 101,
            "name": "Nullable Fields Yarn",
            "permalink": "nullable-fields-yarn",
            "yarn_fibers": None,
            "photos": None,
            "discontinued": None,
        }
        yarn = Yarn.model_validate(data)
        assert yarn.yarn_fibers == []
        assert yarn.photos == []
        assert yarn.discontinued is False

    def test_yarn_company_name_sync(self):
        data = {
            "id": 102,
            "name": "Sync Yarn",
            "permalink": "sync-yarn",
            "yarn_company": {
                "id": 50,
                "name": "Cascade Yarns",
            },
        }
        yarn = Yarn.model_validate(data)
        assert yarn.yarn_company_name == "Cascade Yarns"

    @pytest.mark.parametrize(
        ("field", "invalid_val"),
        [
            ("grams", -5.0),
            ("yardage", -10.0),
            ("rating_average", -0.1),
            ("rating_average", 5.1),
            ("rating_count", -1),
        ],
    )
    def test_yarn_invalid_numeric_values_fail(self, field, invalid_val):
        data = {
            "id": 103,
            "name": "Invalid Yarn",
            "permalink": "invalid-yarn",
            field: invalid_val,
        }
        with pytest.raises(ValidationError):
            Yarn.model_validate(data)

    def test_yarn_empty_name_or_permalink_fails(self):
        with pytest.raises(ValidationError):
            Yarn.model_validate({"id": 1, "name": "   ", "permalink": "yarn-1"})
        with pytest.raises(ValidationError):
            Yarn.model_validate({"id": 1, "name": "Valid Yarn", "permalink": ""})


class TestYarnSearchResult:
    def test_valid_search_result(self):
        data = {
            "id": 2420,
            "name": "Rios",
            "permalink": "malabrigo-yarn-rios",
            "yarn_company_name": "Malabrigo Yarn",
            "grams": 100.0,
            "yardage": 210.0,
            "discontinued": False,
            "min_gauge": 18.0,
            "max_gauge": 22.0,
            "rating_average": 4.78,
            "rating_count": 8940,
        }
        result = YarnSearchResult.model_validate(data)
        assert result.id == 2420
        assert result.name == "Rios"
        assert result.min_gauge == 18.0
        assert result.max_gauge == 22.0

    def test_search_result_gauge_range_validation(self):
        with pytest.raises(ValidationError, match="min_gauge .* cannot be greater than max_gauge"):
            YarnSearchResult.model_validate(
                {
                    "id": 1,
                    "name": "Gauge Mismatch",
                    "permalink": "gauge-mismatch",
                    "min_gauge": 25.0,
                    "max_gauge": 20.0,
                }
            )

    @pytest.mark.parametrize(
        ("field", "invalid_val"),
        [
            ("grams", -1.0),
            ("yardage", -10.0),
            ("wpi", -2),
            ("min_gauge", -5.0),
            ("max_gauge", -5.0),
            ("gauge_divisor", -1),
            ("rating_count", -1),
            ("rating_total", -10),
            ("rating_average", -0.5),
            ("rating_average", 5.5),
        ],
    )
    def test_search_result_invalid_numeric_values_fail(self, field, invalid_val):
        data = {
            "id": 2,
            "name": "Invalid Result",
            "permalink": "invalid-result",
            field: invalid_val,
        }
        with pytest.raises(ValidationError):
            YarnSearchResult.model_validate(data)

    def test_search_result_null_discontinued(self):
        result = YarnSearchResult.model_validate(
            {"id": 3, "name": "Null Discontinued", "permalink": "null-disc", "discontinued": None}
        )
        assert result.discontinued is False


class TestYarnSearchResponse:
    def test_yarn_search_response(self):
        data = {
            "paginator": {
                "page": 1,
                "page_size": 25,
                "page_count": 4,
                "last_page": 4,
                "results": 95,
            },
            "yarns": [
                {
                    "id": 2420,
                    "name": "Rios",
                    "permalink": "malabrigo-yarn-rios",
                    "yarn_company_name": "Malabrigo Yarn",
                    "grams": 100.0,
                    "yardage": 210.0,
                    "discontinued": False,
                    "first_photo": {
                        "id": 12345,
                        "square_url": "https://images.ravelry.com/photo/sq.jpg",
                    },
                    "personal_attributes": {
                        "favorited": True,
                        "bookmark_id": 999,
                    },
                }
            ],
        }
        resp = YarnSearchResponse.model_validate(data)
        assert resp.paginator.results == 95
        assert len(resp.yarns) == 1
        assert resp.yarns[0].name == "Rios"
        assert resp.yarns[0].first_photo is not None
        assert resp.yarns[0].personal_attributes is not None
        assert resp.yarns[0].personal_attributes.favorited is True

    def test_yarn_search_response_null_yarns_defaults_empty(self):
        data = {
            "paginator": {
                "page": 1,
                "page_size": 25,
                "page_count": 0,
                "last_page": 0,
                "results": 0,
            },
            "yarns": None,
        }
        resp = YarnSearchResponse.model_validate(data)
        assert resp.yarns == []

    def test_yarn_search_response_missing_yarns_defaults_empty(self):
        data = {
            "paginator": {
                "page": 1,
                "page_size": 25,
                "page_count": 0,
                "last_page": 0,
                "results": 0,
            }
        }
        resp = YarnSearchResponse.model_validate(data)
        assert resp.yarns == []


class TestYarnDetailResponse:
    def test_yarn_detail_response(self):
        data = {
            "yarn": {
                "id": 2420,
                "name": "Rios",
                "permalink": "malabrigo-yarn-rios",
            }
        }
        resp = YarnDetailResponse.model_validate(data)
        assert resp.yarn.id == 2420
        assert resp.yarn.name == "Rios"

