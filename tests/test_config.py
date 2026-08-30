"""Unit tests for Settings configuration and credential management."""

import pytest
from pydantic import SecretStr

from stashstats.config import Settings


def test_settings_credential_pairs(monkeypatch):
    """Test Settings loads explicit dev and prod credential pairs."""
    monkeypatch.setenv("DEV_USERNAME", "dev_user_123")
    monkeypatch.setenv("DEV_API_KEY", "dev_secret_abc")
    monkeypatch.setenv("PROD_USERNAME", "prod_user_456")
    monkeypatch.setenv("PROD_API_KEY", "prod_secret_xyz")

    s = Settings()
    assert s.dev_username == "dev_user_123"
    assert s.dev_api_key.get_secret_value() == "dev_secret_abc"
    assert s.prod_username == "prod_user_456"
    assert s.prod_api_key.get_secret_value() == "prod_secret_xyz"


def test_settings_auth_tuple_for(monkeypatch):
    """Test Settings.auth_tuple_for returns correct (username, password) tuples."""
    monkeypatch.setenv("DEV_USERNAME", "dev_user_123")
    monkeypatch.setenv("DEV_API_KEY", "dev_secret_abc")
    monkeypatch.setenv("PROD_USERNAME", "prod_user_456")
    monkeypatch.setenv("PROD_API_KEY", "prod_secret_xyz")

    s = Settings()
    assert s.auth_tuple_for("dev") == ("dev_user_123", "dev_secret_abc")
    assert s.auth_tuple_for("prod") == ("prod_user_456", "prod_secret_xyz")


def test_settings_auth_tuple_for_invalid():
    """Test Settings.auth_tuple_for raises ValueError for invalid label."""
    s = Settings()
    with pytest.raises(ValueError, match="Unknown account label"):
        s.auth_tuple_for("invalid_label")
