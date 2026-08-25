"""Interactive Modal component for manually adding custom/unlisted yarn directly to stash."""

from datetime import UTC, datetime
from typing import Any

import dash_bootstrap_components as dbc
from dash import html

DARK_INPUT_STYLE = {
    "backgroundColor": "#2b3035",
    "color": "#fff",
    "borderColor": "#495057",
}

YARN_WEIGHT_OPTIONS = [
    {"label": "-- Select Weight --", "value": ""},
    {"label": "Lace / 2 ply (33-40 wpi)", "value": "Lace"},
    {"label": "Light Fingering / 3 ply", "value": "Light Fingering"},
    {"label": "Fingering / 4 ply (14-18 wpi)", "value": "Fingering"},
    {"label": "Sport / 5 ply (12 wpi)", "value": "Sport"},
    {"label": "DK / 8 ply (11 wpi)", "value": "DK"},
    {"label": "Worsted / 10 ply (9 wpi)", "value": "Worsted"},
    {"label": "Aran / 10 ply (8 wpi)", "value": "Aran"},
    {"label": "Bulky / 12 ply (7 wpi)", "value": "Bulky"},
    {"label": "Super Bulky (5-6 wpi)", "value": "Super Bulky"},
    {"label": "Jumbo (1-4 wpi)", "value": "Jumbo"},
    {"label": "Thread", "value": "Thread"},
    {"label": "Other", "value": "Other"},
]

STATUS_OPTIONS = [
    {"label": "In stash", "value": "In stash"},
    {"label": "Used up", "value": "Used up"},
    {"label": "Will trade/sell", "value": "Will trade/sell"},
    {"label": "Gone / Sold", "value": "Gone / Sold"},
]


def create_manual_yarn_modal(is_open: bool = False) -> dbc.Modal:
    """Create the interactive modal dialog for manually adding yarn to stash.

    Args:
        is_open: Initial visibility state.

    Returns:
        Configured dbc.Modal component.
    """
    today_iso = datetime.now(tz=UTC).date().isoformat()

    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle(
                    [
                        html.I(className="bi bi-plus-circle-fill me-2 text-success"),
                        "Add Yarn Manually to Stash",
                    ]
                ),
                close_button=True,
                className="bg-dark text-light border-secondary",
            ),
            dbc.ModalBody(
                [
                    html.P(
                        "Manually record handspun, unlisted indie dyes, or custom yarns directly into your stash.",
                        className="text-muted small mb-3",
                    ),
                    html.Div(id="manual-yarn-status-msg", className="mb-3"),
                    # Row 1: Yarn Line & Company
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label(
                                        ["Yarn Name / Line ", html.Span("*", className="text-danger")],
                                        className="fw-bold small",
                                    ),
                                    dbc.Input(
                                        id="manual-yarn-name",
                                        type="text",
                                        placeholder="e.g. Rios, Merino Singles, Handspun",
                                        style=DARK_INPUT_STYLE,
                                    ),
                                ],
                                xs=12,
                                sm=6,
                                className="mb-3",
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Brand / Company / Dyer", className="fw-bold small"),
                                    dbc.Input(
                                        id="manual-yarn-brand",
                                        type="text",
                                        placeholder="e.g. Malabrigo, Hedgehog Fibres, Local Mill",
                                        style=DARK_INPUT_STYLE,
                                    ),
                                ],
                                xs=12,
                                sm=6,
                                className="mb-3",
                            ),
                        ]
                    ),
                    # Row 2: Weight & Colorway & Dye Lot
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Yarn Weight", className="fw-bold small"),
                                    dbc.Select(
                                        id="manual-yarn-weight",
                                        options=YARN_WEIGHT_OPTIONS,
                                        value="Worsted",
                                        style=DARK_INPUT_STYLE,
                                    ),
                                ],
                                xs=12,
                                sm=4,
                                className="mb-3",
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Colorway Name / Number", className="fw-bold small"),
                                    dbc.Input(
                                        id="manual-yarn-colorway",
                                        type="text",
                                        placeholder="e.g. Sunset Glow, Diana, #42",
                                        style=DARK_INPUT_STYLE,
                                    ),
                                ],
                                xs=12,
                                sm=4,
                                className="mb-3",
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Dye Lot", className="fw-bold small"),
                                    dbc.Input(
                                        id="manual-yarn-dyelot",
                                        type="text",
                                        placeholder="e.g. Lot A, 2026",
                                        style=DARK_INPUT_STYLE,
                                    ),
                                ],
                                xs=12,
                                sm=4,
                                className="mb-3",
                            ),
                        ]
                    ),
                    # Row 3: Quantities (Skeins, Yards, Grams)
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label(
                                        ["Skeins ", html.Span("*", className="text-danger")],
                                        className="fw-bold small",
                                    ),
                                    dbc.Input(
                                        id="manual-yarn-skeins",
                                        type="number",
                                        value=1.0,
                                        min=0.1,
                                        step=0.5,
                                        style=DARK_INPUT_STYLE,
                                    ),
                                ],
                                xs=12,
                                sm=4,
                                className="mb-3",
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Total Yards", className="fw-bold small"),
                                    dbc.Input(
                                        id="manual-yarn-yards",
                                        type="number",
                                        placeholder="e.g. 210",
                                        min=0,
                                        step=1,
                                        style=DARK_INPUT_STYLE,
                                    ),
                                ],
                                xs=12,
                                sm=4,
                                className="mb-3",
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Total Grams", className="fw-bold small"),
                                    dbc.Input(
                                        id="manual-yarn-grams",
                                        type="number",
                                        placeholder="e.g. 100",
                                        min=0,
                                        step=1,
                                        style=DARK_INPUT_STYLE,
                                    ),
                                ],
                                xs=12,
                                sm=4,
                                className="mb-3",
                            ),
                        ]
                    ),
                    # Row 4: Location, Date & Status
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Storage Location", className="fw-bold small"),
                                    dbc.Input(
                                        id="manual-yarn-location",
                                        type="text",
                                        placeholder="e.g. Bin 3, Cedar Chest, Top Shelf",
                                        style=DARK_INPUT_STYLE,
                                    ),
                                ],
                                xs=12,
                                sm=4,
                                className="mb-3",
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Purchase / Added Date", className="fw-bold small"),
                                    dbc.Input(
                                        id="manual-yarn-date",
                                        type="date",
                                        value=today_iso,
                                        style=DARK_INPUT_STYLE,
                                    ),
                                ],
                                xs=12,
                                sm=4,
                                className="mb-3",
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Status", className="fw-bold small"),
                                    dbc.Select(
                                        id="manual-yarn-status",
                                        options=STATUS_OPTIONS,
                                        value="In stash",
                                        style=DARK_INPUT_STYLE,
                                    ),
                                ],
                                xs=12,
                                sm=4,
                                className="mb-3",
                            ),
                        ]
                    ),
                    # Row 5: Notes & Fiber Content
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Notes & Fiber Details", className="fw-bold small"),
                                    dbc.Textarea(
                                        id="manual-yarn-notes",
                                        placeholder="e.g. 100% Superwash Merino, 4-ply, acquired at fiber festival...",
                                        rows=3,
                                        style=DARK_INPUT_STYLE,
                                    ),
                                ],
                                xs=12,
                                className="mb-2",
                            )
                        ]
                    ),
                ],
                className="bg-dark text-light",
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="manual-yarn-btn-cancel",
                        color="secondary",
                        outline=True,
                        className="me-auto",
                    ),
                    dbc.Button(
                        [html.I(className="bi bi-plus-lg me-1"), "Add to Stash"],
                        id="manual-yarn-btn-submit",
                        color="success",
                        className="px-4 fw-bold",
                    ),
                ],
                className="bg-dark border-secondary",
            ),
        ],
        id="manual-yarn-modal",
        is_open=is_open,
        size="lg",
        centered=True,
        backdrop="static",
    )
