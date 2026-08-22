import json
from unittest.mock import Mock, patch

import pytest
import redis

from stashstats.client import RavelryClient
from stashstats.config import Settings
from stashstats.cache import get_redis_client, cached_yarn_search, cached_yarn_details
from stashstats.models import YarnSearchResponse, YarnDetailResponse

@pytest.fixture
def mock_redis():
    with patch("stashstats.cache.get_redis_client") as mock_get_redis:
        mock_client = Mock(spec=redis.Redis)
        mock_get_redis.return_value = mock_client
        yield mock_client

@pytest.fixture
def dummy_yarn_search_data():
    return {
        "paginator": {"page": 1, "page_size": 50, "page_count": 1, "results": 1, "last_page": 1},
        "yarns": [
            {
                "id": 1,
                "name": "Dummy Yarn",
                "brand": {"id": 1, "name": "Dummy Brand"},
                "permalink": "dummy-yarn"
            }
        ]
    }

def test_yarn_search_caching(mock_redis, dummy_yarn_search_data):
    # Setup cache miss
    mock_redis.get.return_value = None
    
    settings = Settings(access_key="dummy", personal_key="dummy")
    client = RavelryClient(settings=settings)
    
    with patch.object(RavelryClient, 'get', return_value=dummy_yarn_search_data) as mock_get:
        # First call - should hit client.get and set cache
        res = client.search_yarns(query="dummy")
        assert isinstance(res, YarnSearchResponse)
        assert res.yarns[0].name == "Dummy Yarn"
        assert mock_redis.setex.called
        assert mock_get.called
        
        # Setup cache hit
        mock_redis.get.return_value = json.dumps(dummy_yarn_search_data)
        mock_get.reset_mock()
        
        # Second call - should return from cache without calling client.get
        res2 = client.search_yarns(query="dummy")
        assert isinstance(res2, YarnSearchResponse)
        assert res2.yarns[0].name == "Dummy Yarn"
        mock_get.assert_not_called()
