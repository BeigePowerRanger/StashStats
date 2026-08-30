"""Account switch confirmation modal component."""

import dash_bootstrap_components as dbc
from dash import html


def create_account_switch_modal(
    target_label: str = "prod",
    target_username: str | None = None,
    is_open: bool = False,
) -> dbc.Modal:
    """Create a confirmation modal for toggling between DEV and PROD Ravelry accounts.

    Args:
        target_label: Target environment label ('dev' or 'prod').
        target_username: Optional target username to display.
        is_open: Initial open state of modal.

    Returns:
        Configured dbc.Modal component.
    """
    target_display = target_label.upper()
    user_str = f" (@{target_username})" if target_username else ""

    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle(
                    [
                        html.I(className="bi bi-arrow-left-right me-2 text-warning"),
                        "Switch Ravelry Account",
                    ]
                ),
                close_button=True,
                className="bg-dark text-light border-secondary",
            ),
            dbc.ModalBody(
                [
                    html.P(
                        f"Switch active session to {target_display} account{user_str}?",
                        className="fw-semibold fs-5 mb-2",
                    ),
                    html.P(
                        "All currently loaded stash items, projects, and analytics data will reload with the new account credentials.",
                        className="text-muted small mb-0",
                    ),
                ],
                id="account-switch-modal-body",
                className="bg-dark text-light border-secondary py-3",
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="account-switch-cancel-btn",
                        color="secondary",
                        outline=True,
                        className="me-2",
                    ),
                    dbc.Button(
                        [
                            html.I(className="bi bi-check-circle me-1"),
                            f"Switch to {target_display}",
                        ],
                        id="account-switch-confirm-btn",
                        color="warning" if target_display == "DEV" else "danger",
                        className="fw-semibold",
                    ),
                ],
                className="bg-dark text-light border-secondary",
            ),
        ],
        id="account-switch-modal",
        is_open=is_open,
        centered=True,
        backdrop="static",
    )
