import pytest
from unittest.mock import Mock, patch

@pytest.fixture(autouse=True)
def disable_redis_cache():
    with patch("stashstats.cache.get_redis_client") as mock_get_redis:
        mock_client = Mock()
        mock_client.get.return_value = None
        mock_get_redis.return_value = mock_client
        yield mock_client


@pytest.fixture(autouse=True)
def mock_default_account_manager():
    mock_client = Mock()
    mock_client._cached_username = "testuser"
    mock_client.username = "testuser"
    mock_client.get_all_my_stash.return_value = []
    mock_client.get_my_stash.return_value = Mock(stash=[])
    mock_client.get_my_projects.return_value = Mock(projects=[])
    with patch("stashstats.auth.account_manager.get_client", return_value=mock_client):
        yield mock_client
