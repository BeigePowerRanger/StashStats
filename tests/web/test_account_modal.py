"""Unit tests for Account Switch Modal component in stashstats.web."""

from stashstats.web.components.account_modal import create_account_switch_modal
from tests.web.test_header import find_component_by_id


def test_create_account_switch_modal_structure():
    """Verify modal has expected id, title, buttons, and target text."""
    modal = create_account_switch_modal(target_label="prod", target_username="ProdUser")
    assert modal is not None
    assert getattr(modal, "id", None) == "account-switch-modal"
    assert getattr(modal, "is_open", None) is False

    confirm_btn = find_component_by_id(modal, "account-switch-confirm-btn")
    assert confirm_btn is not None

    cancel_btn = find_component_by_id(modal, "account-switch-cancel-btn")
    assert cancel_btn is not None

    body = find_component_by_id(modal, "account-switch-modal-body")
    assert body is not None
    json_repr = str(body.to_plotly_json())
    assert "PROD" in json_repr
