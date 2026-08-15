
from stashstats.models.yarn import (
    Colorway,
    FiberType,
    Yarn,
    YarnDetailResponse,
    YarnFiber,
    YarnSearchResponse,
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


class TestColorway:
    def test_colorway_with_family(self):
        cw = Colorway.model_validate({"id": 101, "name": "Frank Ochre", "color_family_id": 3})
        assert cw.id == 101
        assert cw.name == "Frank Ochre"
        assert cw.color_family_id == 3

    def test_colorway_without_family(self):
        cw = Colorway.model_validate({"id": 102, "name": "Custom Dye"})
        assert cw.color_family_id is None


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
