"""Global navigation header component for StashStats."""

import dash_bootstrap_components as dbc
from dash import html


def create_header(
    username: str | None = None,
    sync_status: str = "Synced",
    pending_count: int = 0,
    last_synced: str | None = None,
) -> html.Div:
    """Create global header for StashStats with logo, greeting, and meta chips.

    Args:
        username: Authenticated Ravelry username, or None for guest/offline.
        sync_status: Text status for sync state (e.g. 'Synced', 'Offline').
        pending_count: Count of pending local mutations to sync.
        last_synced: Optional timestamp string of last successful sync.

    Returns:
        Configured header component.
    """
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

    meta_chips = dbc.Row(
        dbc.Col(
            html.Div(
                [sync_container, user_badge],
                className="d-flex align-items-center justify-content-end",
            ),
            width=12,
        ),
        className="px-3 pt-2",
    )

    logo_img = html.Img(
        src="/assets/Images/logo_color.png",
        alt="StashStats",
        id="header-logo",
        style={"width": "100%", "maxWidth": "500px", "maxHeight": "165px", "objectFit": "contain"},
    )

    logo_row = dbc.Row(
        dbc.Col(logo_img, width="auto", className="text-center"),
        justify="center",
        className="justify-content-center align-items-center my-2",
        id="header-brand",
    )

    children: list[html.Component] = [
        meta_chips,
        logo_row,
    ]

    if username:
        greeting_row = dbc.Row(
            dbc.Col(
                html.H5(
                    f"Hello {username}!",
                    className="text-info text-center mt-2",
                    id="header-greeting",
                ),
                width=12,
            ),
            justify="center",
            className="justify-content-center align-items-center",
        )
        children.append(greeting_row)

    children.append(html.Hr(style={"margin": "20px 0"}))

    return html.Div(
        children=children,
        id="global-header",
        className="w-100",
    )
