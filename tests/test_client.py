from typing import Any

import httpx
import pytest

from stashstats.client import RavelryClient
from stashstats.config import Settings
from stashstats.models.stash import Pack, StashItem


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
