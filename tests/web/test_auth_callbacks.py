"""Tests for account switch callbacks and state management."""

from unittest.mock import MagicMock, patch
import dash
import pytest

from stashstats.auth import AccountManager
from stashstats.config import Settings
from stashstats.models import CurrentUserResponse
from stashstats.models.project import ProjectListResponse, ProjectListResult
from stashstats.models.stash import StashItem, StashListResponse
from stashstats.models.user import UserProfile
from stashstats.web.callbacks.auth import (
    handle_account_modal_toggle_logic,
    handle_account_switch_confirm_logic,
    register_auth_callbacks,
)


@pytest.fixture
def mock_mgr(monkeypatch):
    monkeypatch.setenv("DEV_USERNAME", "dev_acc")
    monkeypatch.setenv("DEV_API_KEY", "dev_sec")
    monkeypatch.setenv("PROD_USERNAME", "prod_acc")
    monkeypatch.setenv("PROD_API_KEY", "prod_sec")
    s = Settings()
    return AccountManager(settings=s, auto_init=False)


def test_handle_account_modal_toggle_open(mock_mgr):
    """Test clicking user badge opens modal with target environment details."""
    is_open, body, btn_children, btn_color = handle_account_modal_toggle_logic(
        badge_clicks=1,
        cancel_clicks=None,
        is_open=False,
        account_mgr=mock_mgr,
        triggered_id="header-user-badge",
    )
    assert is_open is True
    assert "PROD" in str(body)
    assert "PROD" in str(btn_children)


def test_handle_account_modal_toggle_cancel(mock_mgr):
    """Test clicking cancel button closes modal."""
    is_open, body, btn_children, btn_color = handle_account_modal_toggle_logic(
        badge_clicks=1,
        cancel_clicks=1,
        is_open=True,
        account_mgr=mock_mgr,
        triggered_id="account-switch-cancel-btn",
    )
    assert is_open is False


def test_handle_account_modal_toggle_prevent_update(mock_mgr):
    """Test no clicks raises PreventUpdate."""
    with pytest.raises(dash.exceptions.PreventUpdate):
        handle_account_modal_toggle_logic(
            badge_clicks=None,
            cancel_clicks=None,
            is_open=False,
            account_mgr=mock_mgr,
            triggered_id=None,
        )


@patch("stashstats.client.ravelry_client.RavelryClient.get_current_user")
def test_handle_account_switch_confirm_success(mock_get_user, mock_mgr):
    """Test confirming switch re-initializes client, re-fetches stash and projects, and updates UI."""
    mock_get_user.return_value = CurrentUserResponse(user=UserProfile(id=99, username="ProdKnitPro"))

    mock_client = MagicMock()
    mock_client.username = "ProdKnitPro"
    mock_client._cached_username = "ProdKnitPro"
    mock_client.get_all_my_stash.return_value = [
        StashItem(id=101, name="Silk Merino", skeins=2.0)
    ]
    mock_client.get_my_projects.return_value = ProjectListResponse(
        projects=[ProjectListResult(id=201, name="Winter Scarf", progress=80)],
        paginator={"page_count": 1, "page": 1, "page_size": 50, "results": 1, "last_page": 1},
    )

    with patch.object(mock_mgr, "get_client", return_value=mock_client):
        (
            modal_open,
            badge_children,
            greeting_text,
            greeting_style,
            stash_data,
            projects_data,
            user_store_data,
        ) = handle_account_switch_confirm_logic(
            n_clicks=1,
            account_mgr=mock_mgr,
        )

    assert modal_open is False
    assert mock_mgr.get_active_label() == "prod"
    assert "ProdKnitPro" in str(badge_children)
    assert "PROD" in str(badge_children)
    assert greeting_text == "Hello ProdKnitPro!"
    assert greeting_style == {}
    assert len(stash_data) == 1
    assert stash_data[0]["id"] == 101
    assert len(projects_data) == 1
    assert projects_data[0]["id"] == 201
    assert user_store_data == {"user_id": "ProdKnitPro"}


def test_handle_account_switch_confirm_prevent_update(mock_mgr):
    """Test confirming with no clicks raises PreventUpdate."""
    with pytest.raises(dash.exceptions.PreventUpdate):
        handle_account_switch_confirm_logic(
            n_clicks=None,
            account_mgr=mock_mgr,
        )
