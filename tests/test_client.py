from typing import Any

import httpx
import pytest

from stashstats.client import RavelryClient
from stashstats.config import Settings
from stashstats.models.stash import Pack, StashItem
from stashstats.models.yarn import YarnDetailResponse, YarnSearchResponse


@pytest.fixture
def mock_settings():
    return Settings(
        username="testuser",
        password="testpassword",
        base_url="https://api.ravelry.com",
    )


class MockTransport(httpx.BaseTransport):
    def __init__(self, handler):
        self.handler = handler

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        return self.handler(request)


class TestRavelryClientCore:
    def test_get_current_user(self, mock_settings):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/current_user.json"
            return httpx.Response(
                200,
                json={"user": {"id": 1, "username": "knitter1"}},
            )

        client = RavelryClient(settings=mock_settings)
        client._client = httpx.Client(
            transport=MockTransport(handler),
            base_url=client.base_url,
            auth=client.auth,
        )

        res = client.get_current_user()
        assert res.user.username == "knitter1"
        assert client._cached_username == "knitter1"


class TestAppDataAPI:
    def test_get_app_data(self, mock_settings):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/app/data/get.json"
            assert request.url.params["keys"] == "key1 key2"
            return httpx.Response(
                200,
                json={"data": {"key1": "val1", "key2": "val2"}},
            )

        client = RavelryClient(settings=mock_settings)
        client._client = httpx.Client(
            transport=MockTransport(handler),
            base_url=client.base_url,
            auth=client.auth,
        )

        data = client.get_app_data(["key1", "key2"])
        assert data["key1"] == "val1"
        assert data["key2"] == "val2"

    def test_set_app_data(self, mock_settings):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/app/data/set.json"
            assert request.url.params["my_key"] == "my_val"
            return httpx.Response(
                200,
                json={"data": {"my_key": "my_val"}},
            )

        client = RavelryClient(settings=mock_settings)
        client._client = httpx.Client(
            transport=MockTransport(handler),
            base_url=client.base_url,
            auth=client.auth,
        )

        res = client.set_app_data(my_key="my_val")
        assert res["my_key"] == "my_val"

    def test_delete_app_data(self, mock_settings):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/app/data/delete.json"
            assert request.url.params["keys"] == "old_key"
            return httpx.Response(
                200,
                json={"data": {"old_key": "deleted"}},
            )

        client = RavelryClient(settings=mock_settings)
        client._client = httpx.Client(
            transport=MockTransport(handler),
            base_url=client.base_url,
            auth=client.auth,
        )

        res = client.delete_app_data(["old_key"])
        assert res["old_key"] == "deleted"


class TestStashHistoryAndDeduplication:
    def test_get_stash_history_empty(self, mock_settings):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"data": {}})

        client = RavelryClient(settings=mock_settings)
        client._client = httpx.Client(
            transport=MockTransport(handler),
            base_url=client.base_url,
            auth=client.auth,
        )

        hist = client.get_stash_history(100)
        assert hist.stash_id == 100
        assert hist.entries == []

    def test_get_batch_stash_history(self, mock_settings):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "data": {
                        "stash_history_101": '{"stash_id": 101, "entries": [{"timestamp": "2024/01/01 10:00:00 +0000", "skeins": 2.0, "total_grams": 200.0, "total_yards": 400.0}]}',
                        "stash_history_102": '{"stash_id": 102, "entries": []}',
                    }
                },
            )

        client = RavelryClient(settings=mock_settings)
        client._client = httpx.Client(
            transport=MockTransport(handler),
            base_url=client.base_url,
            auth=client.auth,
        )

        histories = client.get_batch_stash_history([101, 102, 103])
        assert len(histories) == 3
        assert len(histories[101].entries) == 1
        assert histories[101].entries[0].skeins == 2.0
        assert histories[102].entries == []
        assert histories[103].entries == []

    def test_record_stash_snapshot_new_entry(self, mock_settings):
        calls: list[dict[str, Any]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append({"method": request.method, "path": request.url.path, "params": dict(request.url.params)})
            if request.url.path == "/app/data/get.json":
                return httpx.Response(200, json={"data": {}})
            if request.url.path == "/app/data/set.json":
                return httpx.Response(200, json={"data": dict(request.url.params)})
            return httpx.Response(404)

        client = RavelryClient(settings=mock_settings)
        client._client = httpx.Client(
            transport=MockTransport(handler),
            base_url=client.base_url,
            auth=client.auth,
        )

        item = StashItem(
            id=500,
            permalink="test-item",
            primary_pack=Pack(id=1, skeins=3.0, total_grams=300.0, total_yards=600.0),
            updated_at="2024/05/15 12:00:00 +0000",
        )

        hist = client.record_stash_snapshot(item)
        assert len(hist.entries) == 1
        assert hist.entries[0].skeins == 3.0
        assert hist.entries[0].total_grams == 300.0
        assert hist.entries[0].total_yards == 600.0
        assert any(c["path"] == "/app/data/set.json" for c in calls)

    def test_record_stash_snapshot_deduplication(self, mock_settings):
        set_calls: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/app/data/get.json":
                return httpx.Response(
                    200,
                    json={
                        "data": {
                            "stash_history_500": '{"stash_id": 500, "entries": [{"timestamp": "2024/05/01 12:00:00 +0000", "skeins": 3.0, "total_grams": 300.0, "total_yards": 600.0}]}'
                        }
                    },
                )
            if request.url.path == "/app/data/set.json":
                set_calls.append(request.url.query.decode())
                return httpx.Response(200, json={"data": {}})
            return httpx.Response(404)

        client = RavelryClient(settings=mock_settings)
        client._client = httpx.Client(
            transport=MockTransport(handler),
            base_url=client.base_url,
            auth=client.auth,
        )

        item = StashItem(
            id=500,
            permalink="test-item",
            primary_pack=Pack(id=1, skeins=3.0, total_grams=300.0, total_yards=600.0),
            updated_at="2024/05/15 12:00:00 +0000",
        )

        hist = client.record_stash_snapshot(item)
        # Should not append a duplicate since skeins/grams/yards are identical
        assert len(hist.entries) == 1
        assert len(set_calls) == 0

    def test_delete_stash_history(self, mock_settings):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/app/data/delete.json"
            assert request.url.params["keys"] == "stash_history_777"
            return httpx.Response(200, json={"data": {"stash_history_777": "deleted"}})

        client = RavelryClient(settings=mock_settings)
        client._client = httpx.Client(
            transport=MockTransport(handler),
            base_url=client.base_url,
            auth=client.auth,
        )

        res = client.delete_stash_history(777)
        assert "stash_history_777" in res

    def test_stash_history_key_namespacing(self, mock_settings):
        client = RavelryClient(settings=mock_settings)
        assert client._stash_history_key(123) == "stash_history_123"
        assert client._stash_history_key(123, user_id="alice") == "user_alice_stash_history_123"
        assert client._stash_history_key(123, user_id=456) == "user_456_stash_history_123"

    def test_get_stash_history_with_user_id(self, mock_settings):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params["keys"] == "user_alice_stash_history_999"
            return httpx.Response(
                200,
                json={
                    "data": {
                        "user_alice_stash_history_999": '{"stash_id": 999, "entries": [{"timestamp": "2024/06/01 10:00:00 +0000", "skeins": 1.0, "total_grams": 100.0, "total_yards": 200.0}]}'
                    }
                },
            )

        client = RavelryClient(settings=mock_settings)
        client._client = httpx.Client(
            transport=MockTransport(handler),
            base_url=client.base_url,
            auth=client.auth,
        )

        hist = client.get_stash_history(999, user_id="alice")
        assert hist.stash_id == 999
        assert len(hist.entries) == 1
        assert hist.entries[0].skeins == 1.0


class TestYarnAPI:
    def test_search_yarns_default(self, mock_settings):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/yarns/search.json"
            assert request.url.params["query"] == "Cascade 220"
            assert request.url.params["page"] == "1"
            assert request.url.params["page_size"] == "50"
            assert request.url.params["sort"] == "best"
            assert "personal_attributes" not in request.url.params
            return httpx.Response(
                200,
                json={
                    "paginator": {
                        "page": 1,
                        "page_size": 50,
                        "page_count": 1,
                        "last_page": 1,
                        "results": 1,
                    },
                    "yarns": [
                        {
                            "id": 1001,
                            "name": "Cascade 220",
                            "permalink": "cascade-220",
                            "yarn_company_name": "Cascade Yarns",
                            "rating_average": 4.5,
                            "rating_count": 500,
                        }
                    ],
                },
            )

        client = RavelryClient(settings=mock_settings)
        client._client = httpx.Client(
            transport=MockTransport(handler),
            base_url=client.base_url,
            auth=client.auth,
        )

        res = client.search_yarns("Cascade 220")
        assert isinstance(res, YarnSearchResponse)
        assert res.paginator.results == 1
        assert len(res.yarns) == 1
        assert res.yarns[0].id == 1001
        assert res.yarns[0].name == "Cascade 220"
        assert res.yarns[0].yarn_company_name == "Cascade Yarns"

    def test_search_yarns_with_params(self, mock_settings):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/yarns/search.json"
            assert request.url.params["query"] == "merino"
            assert request.url.params["page"] == "2"
            assert request.url.params["page_size"] == "20"
            assert request.url.params["sort"] == "rating"
            assert request.url.params["personal_attributes"] == "1"
            return httpx.Response(
                200,
                json={
                    "paginator": {
                        "page": 2,
                        "page_size": 20,
                        "page_count": 5,
                        "last_page": 5,
                        "results": 100,
                    },
                    "yarns": [
                        {
                            "id": 2002,
                            "name": "Merino Extrafine",
                            "permalink": "merino-extrafine",
                            "yarn_company_name": "Drops",
                            "first_photo": {
                                "id": 555,
                                "square_url": "https://images.ravelry.com/photo.jpg",
                            },
                            "personal_attributes": {
                                "favorited": True,
                                "bookmark_id": 42,
                            },
                        }
                    ],
                },
            )

        client = RavelryClient(settings=mock_settings)
        client._client = httpx.Client(
            transport=MockTransport(handler),
            base_url=client.base_url,
            auth=client.auth,
        )

        res = client.search_yarns(
            "merino",
            page=2,
            page_size=20,
            sort="rating",
            personal_attributes=True,
        )
        assert isinstance(res, YarnSearchResponse)
        assert res.paginator.page == 2
        assert res.paginator.page_size == 20
        assert len(res.yarns) == 1
        assert res.yarns[0].id == 2002
        assert res.yarns[0].first_photo is not None
        assert res.yarns[0].first_photo.square_url == "https://images.ravelry.com/photo.jpg"
        assert res.yarns[0].personal_attributes is not None
        assert res.yarns[0].personal_attributes.favorited is True

    def test_get_yarn_details(self, mock_settings):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/yarns/2420.json"
            return httpx.Response(
                200,
                json={
                    "yarn": {
                        "id": 2420,
                        "name": "Rios",
                        "permalink": "malabrigo-yarn-rios",
                        "yarn_company_name": "Malabrigo Yarn",
                    }
                },
            )

        client = RavelryClient(settings=mock_settings)
        client._client = httpx.Client(
            transport=MockTransport(handler),
            base_url=client.base_url,
            auth=client.auth,
        )

        res = client.get_yarn_details(2420)
        assert isinstance(res, YarnDetailResponse)
        assert res.yarn.id == 2420
        assert res.yarn.name == "Rios"


class TestRavelryClientProjects:
    def test_get_project_list(self, mock_settings):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/people/knitter1/projects/list.json"
            assert request.url.params["page"] == "1"
            assert request.url.params["page_size"] == "50"
            return httpx.Response(
                200,
                json={
                    "projects": [
                        {
                            "id": 101,
                            "name": "Cozy Beanie",
                            "status_name": "In progress",
                            "progress": 60,
                            "craft_name": "Knitting",
                        }
                    ],
                    "paginator": {
                        "page_count": 1,
                        "page": 1,
                        "page_size": 50,
                        "results": 1,
                        "last_page": 1,
                    },
                },
            )

        client = RavelryClient(settings=mock_settings)
        client._client = httpx.Client(
            transport=MockTransport(handler),
            base_url=client.base_url,
            auth=client.auth,
        )

        res = client.get_project_list("knitter1")
        assert len(res.projects) == 1
        assert res.projects[0].id == 101
        assert res.projects[0].name == "Cozy Beanie"
        assert res.projects[0].progress == 60
        assert res.projects[0].status_name == "In progress"

    def test_get_my_projects(self, mock_settings):
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/current_user.json":
                return httpx.Response(200, json={"user": {"id": 1, "username": "knitter1"}})
            assert request.url.path == "/people/knitter1/projects/list.json"
            return httpx.Response(
                200,
                json={
                    "projects": [
                        {
                            "id": 102,
                            "name": "Wool Socks",
                            "status_name": "Finished",
                            "progress": 100,
                        }
                    ],
                    "paginator": {
                        "page_count": 1,
                        "page": 1,
                        "page_size": 50,
                        "results": 1,
                        "last_page": 1,
                    },
                },
            )

        client = RavelryClient(settings=mock_settings)
        client._client = httpx.Client(
            transport=MockTransport(handler),
            base_url=client.base_url,
            auth=client.auth,
        )

        res = client.get_my_projects()
        assert len(res.projects) == 1
        assert res.projects[0].id == 102
        assert res.projects[0].name == "Wool Socks"

    def test_get_project(self, mock_settings):
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/current_user.json":
                return httpx.Response(200, json={"user": {"id": 1, "username": "knitter1"}})
            assert request.url.path == "/projects/knitter1/101.json"
            return httpx.Response(
                200,
                json={
                    "project": {
                        "id": 101,
                        "name": "Cozy Beanie",
                        "status_name": "In progress",
                        "progress": 60,
                        "notes": "Using size 7 needles",
                    },
                    "comments": [],
                },
            )

        client = RavelryClient(settings=mock_settings)
        client._client = httpx.Client(
            transport=MockTransport(handler),
            base_url=client.base_url,
            auth=client.auth,
        )

        res = client.get_project(101)
        assert res.project.id == 101
        assert res.project.notes == "Using size 7 needles"

