from stashstats.models.stash import (
    Pack,
    StashDetailResponse,
    StashItem,
    StashListResponse,
    StashSearchResponse,
    StashStatus,
    StashYarn,
)


class TestStashStatus:
    def test_stash_status(self):
        ss = StashStatus.model_validate({"id": 1, "name": "In stash"})
        assert ss.id == 1
        assert ss.name == "In stash"


class TestPack:
    def test_full_pack(self):
        data = {
            "id": 555,
            "stash_id": 1234,
            "yarn_id": 2420,
            "colorway": "Whales Road",
            "dye_lot": "2024-A",
            "skeins": 3.5,
            "total_grams": 350.0,
            "total_yards": 735.0,
            "total_meters": 672.0,
            "total_ounces": 12.35,
            "grams_per_skein": 100.0,
            "yards_per_skein": 210.0,
            "meters_per_skein": 192.0,
            "ounces_per_skein": 3.53,
            "quantity_description": "3.5 skeins = 735.0 yards",
            "shop_name": "Local Yarn Store",
            "purchased_date": "2024-05-15",
        }
        pack = Pack.model_validate(data)
        assert pack.id == 555
        assert pack.skeins == 3.5
        assert pack.colorway == "Whales Road"
        assert pack.shop_name == "Local Yarn Store"
        assert pack.purchased_date == "2024-05-15"

    def test_minimal_pack(self):
        pack = Pack.model_validate({"id": 1})
        assert pack.id == 1
        assert pack.skeins is None
        assert pack.colorway is None


class TestStashYarn:
    def test_stash_yarn(self):
        data = {
            "id": 2420,
            "name": "Rios",
            "yarn_company_name": "Malabrigo Yarn",
            "yarn_weight": {"id": 5, "name": "Worsted"},
            "photos": [{"id": 10, "square_url": "https://images.ravelry.com/photo.jpg"}],
        }
        sy = StashYarn.model_validate(data)
        assert sy.id == 2420
        assert sy.name == "Rios"
        assert sy.yarn_weight is not None
        assert sy.yarn_weight.name == "Worsted"
        assert len(sy.photos) == 1


class TestStashItem:
    def test_full_stash_item(self):
        data = {
            "id": 9999,
            "name": "My Malabrigo Stash",
            "permalink": "thotsky-malabrigo-rios",
            "colorway_name": "Whales Road",
            "color_family_name": "Blue",
            "dye_lot": "2024-A",
            "location": "Top Shelf Bin 2",
            "comments_count": 2,
            "favorites_count": 5,
            "handspun": False,
            "has_photo": True,
            "created_at": "2024/01/15 10:00:00 -0500",
            "updated_at": "2024/06/20 14:30:00 -0500",
            "tag_names": ["sweater-quantity", "favorite"],
            "yarn_weight_name": "Worsted",
            "stash_status": {"id": 1, "name": "In stash"},
            "yarn": {
                "id": 2420,
                "name": "Rios",
                "yarn_company_name": "Malabrigo Yarn",
            },
            "primary_pack": {
                "id": 555,
                "skeins": 4.0,
                "total_grams": 400.0,
                "total_yards": 840.0,
            },
            "packs": [
                {
                    "id": 555,
                    "skeins": 4.0,
                    "total_grams": 400.0,
                    "total_yards": 840.0,
                }
            ],
            "first_photo": {
                "id": 777,
                "medium_url": "https://images.ravelry.com/photo_med.jpg",
            },
            "user": {
                "id": 12345,
                "username": "thotsky",
            },
        }
        item = StashItem.model_validate(data)
        assert item.id == 9999
        assert item.permalink == "thotsky-malabrigo-rios"
        assert item.stash_status is not None
        assert item.stash_status.name == "In stash"
        assert item.yarn is not None
        assert item.yarn.name == "Rios"
        assert item.primary_pack is not None
        assert item.primary_pack.total_yards == 840.0
        assert len(item.packs) == 1
        assert len(item.tag_names) == 2
        assert item.user is not None
        assert item.user.username == "thotsky"


class TestStashEnvelopes:
    def test_stash_list_response(self):
        data = {
            "paginator": {
                "page": 1,
                "page_size": 25,
                "page_count": 1,
                "last_page": 1,
                "results": 1,
            },
            "stash": [
                {
                    "id": 123,
                    "permalink": "stash-123",
                }
            ],
        }
        resp = StashListResponse.model_validate(data)
        assert resp.paginator.results == 1
        assert len(resp.stash) == 1
        assert resp.stash[0].id == 123

    def test_stash_detail_response(self):
        data = {
            "stash": {
                "id": 123,
                "permalink": "stash-123",
            }
        }
        resp = StashDetailResponse.model_validate(data)
        assert resp.stash.id == 123

    def test_stash_search_response(self):
        data = {
            "paginator": {
                "page": 1,
                "page_size": 25,
                "page_count": 1,
                "last_page": 1,
                "results": 0,
            },
            "stashes": [],
        }
        resp = StashSearchResponse.model_validate(data)
        assert resp.stashes == []
