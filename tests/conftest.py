import pytest
from unittest.mock import Mock, patch

@pytest.fixture(autouse=True)
def disable_redis_cache():
    with patch("stashstats.cache.get_redis_client") as mock_get_redis:
        mock_client = Mock()
        mock_client.get.return_value = None
        mock_get_redis.return_value = mock_client
        yield mock_client
