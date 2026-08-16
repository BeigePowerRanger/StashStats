"""Global navigation header component for StashStats."""

import dash_bootstrap_components as dbc
from dash import html


def create_header(
    username: str | None = None,
    sync_status: str = "Synced",
    pending_count: int = 0,
    last_synced: str | None = None,
) -> dbc.Navbar:
    """Create global navbar header for StashStats.

    Args:
        username: Authenticated Ravelry username, or None for guest/offline.
        sync_status: Text status for sync state (e.g. 'Synced', 'Offline').
        pending_count: Count of pending local mutations to sync.
        last_synced: Optional timestamp string of last successful sync.

    Returns:
        Configured dbc.Navbar component.
    """
    brand_content = [
        html.I(className="bi bi-box-seam me-2 text-success"),
        html.Span("StashStats", className="fw-bold"),
    ]

    brand_element = dbc.NavbarBrand(
        children=brand_content,
        href="#",
        className="d-flex align-items-center text-decoration-none fs-4 text-white",
        id="header-brand",
    )

    user_label = f"@{username}" if username else "@Guest"
    user_badge = dbc.Badge(
        user_label,
        color="info",
        pill=True,
        className="ms-2 px-2 py-1 fs-6 align-self-center",
        id="header-user-badge",
    )

    if pending_count > 0:
        sync_badge_text = f"{pending_count} pending"
        sync_badge_color = "warning"
    else:
        sync_badge_text = sync_status
        sync_badge_color = "success"

    sync_badge = dbc.Badge(
        sync_badge_text,
        color=sync_badge_color,
        pill=True,
        className="ms-2 px-2 py-1 align-self-center",
        id="header-sync-badge",
    )

    sync_elements: list[html.Component] = [
        sync_badge,
    ]

    if last_synced:
        sync_elements.append(
            html.Small(
                f"Last synced: {last_synced}",
                className="text-muted ms-2 align-self-center",
                id="header-last-synced",
            )
        )

    sync_container = html.Div(
        children=sync_elements,
        className="d-flex align-items-center",
        id="header-sync-indicator",
    )

    right_col = html.Div(
        children=[
            sync_container,
            user_badge,
        ],
        className="d-flex align-items-center ms-auto",
    )

    return dbc.Navbar(
        dbc.Container(
            [
                brand_element,
                right_col,
            ],
            fluid=True,
            className="px-3",
        ),
        color="dark",
        dark=True,
        className="border-bottom border-secondary py-2",
        id="global-header",
    )
