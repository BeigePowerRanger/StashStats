"""Unit tests for AccountManager authentication and account switching."""

from unittest.mock import MagicMock, patch
import pytest

from stashstats.auth import AccountManager
from stashstats.config import Settings
from stashstats.models.user import CurrentUserResponse, UserProfile


@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setenv("DEV_USERNAME", "dev_access_123")
    monkeypatch.setenv("DEV_API_KEY", "dev_secret_abc")
    monkeypatch.setenv("PROD_USERNAME", "prod_access_456")
    monkeypatch.setenv("PROD_API_KEY", "prod_secret_xyz")
    return Settings()


def test_account_manager_defaults_to_dev(mock_settings):
    """Test AccountManager defaults to 'dev' environment on init."""
    mgr = AccountManager(settings=mock_settings, auto_init=False)
    assert mgr.get_active_label() == "dev"
    assert mgr.get_target_label() == "prod"


def test_account_manager_get_client(mock_settings):
    """Test get_client returns a configured RavelryClient."""
    mgr = AccountManager(settings=mock_settings, auto_init=False)
    client = mgr.get_client()
    assert client.settings.access_key == "dev_access_123"
    assert client.settings.personal_key.get_secret_value() == "dev_secret_abc"
    assert client.auth == ("dev_access_123", "dev_secret_abc")


@patch("stashstats.client.ravelry_client.RavelryClient.get_current_user")
def test_account_manager_switch(mock_get_user, mock_settings):
    """Test switch toggles between dev and prod and re-initializes client."""
    mock_get_user.return_value = CurrentUserResponse(user=UserProfile(id=1, username="DevYarnLover"))

    mgr = AccountManager(settings=mock_settings, auto_init=False)
    assert mgr.get_active_label() == "dev"

    # Switch to prod
    mock_get_user.return_value = CurrentUserResponse(user=UserProfile(id=2, username="ProdKnitMaster"))
    new_label, username = mgr.switch()

    assert new_label == "prod"
    assert mgr.get_active_label() == "prod"
    assert mgr.get_target_label() == "dev"
    assert client_settings_key(mgr) == "prod_access_456"
    assert client_settings_secret(mgr) == "prod_secret_xyz"
    assert username == "ProdKnitMaster"

    # Switch back to dev
    mock_get_user.return_value = CurrentUserResponse(user=UserProfile(id=1, username="DevYarnLover"))
    new_label, username = mgr.switch()
    assert new_label == "dev"
    assert mgr.get_active_label() == "dev"
    assert mgr.get_target_label() == "prod"
    assert client_settings_key(mgr) == "dev_access_123"


def client_settings_key(mgr: AccountManager) -> str:
    return mgr.get_client().settings.access_key


def client_settings_secret(mgr: AccountManager) -> str:
    return mgr.get_client().settings.personal_key.get_secret_value()


def test_account_manager_switch_invalid(mock_settings):
    """Test switch raises ValueError on invalid label."""
    mgr = AccountManager(settings=mock_settings, auto_init=False)
    with pytest.raises(ValueError, match="Unknown account label"):
        mgr.switch("staging")
