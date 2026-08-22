"""Personal Stash grouped accordion components, parent-yarn grouping engine, and row renderers."""

import math
from typing import Any

import dash_bootstrap_components as dbc
from dash import html
from pydantic import BaseModel, Field

from stashstats.models.stash import StashItem


class ParentYarnGroup(BaseModel):
    """Aggregate model representing all stash records sharing a parent yarn brand and product name."""

    brand_name: str
    yarn_name: str
    display_title: str
    items: list[StashItem] = Field(default_factory=list)
    total_items: int = 0
    total_skeins: float = 0.0
    total_yards: float = 0.0
    total_meters: float = 0.0
    total_grams: float = 0.0
    photo_url: str | None = None
    latest_date: str | None = None
    group_key: str = ""


def _resolve_brand_and_yarn(item: StashItem) -> tuple[str, str]:
    """Resolve brand name and yarn product name from a StashItem."""
    if item.yarn:
        brand = (
            item.yarn.yarn_company_name
            or (item.yarn.yarn_company.name if item.yarn.yarn_company else None)
            or "Unknown Brand"
        )
        yarn = item.yarn.name or item.name or "Uncategorized"
    elif item.name:
        brand = "Custom / Unlinked"
        yarn = item.name
    else:
        brand = "Custom / Unlinked"
        yarn = "Uncategorized"
    return brand, yarn


def _resolve_photo_url(item: StashItem) -> str | None:
    """Resolve the highest quality thumbnail photo URL for a stash item or yarn."""
    if item.yarn and item.yarn.photos:
        p = item.yarn.photos[0]
        return p.square_url or p.small_url or p.medium_url or p.thumbnail_url
    if item.first_photo:
        p = item.first_photo
        return p.square_url or p.small_url or p.medium_url or p.thumbnail_url
    return None


def _resolve_item_date(item: StashItem) -> str:
    """Extract the most relevant timestamp for sorting."""
    if item.created_at:
        return item.created_at
    if item.primary_pack and item.primary_pack.purchased_date:
        return item.primary_pack.purchased_date
    if item.updated_at:
        return item.updated_at
    return ""


def group_stash_items(items: list[StashItem] | list[dict[str, Any]]) -> list[ParentYarnGroup]:
    """Group stash records by parent yarn (Brand + Product Name) and compute aggregate metrics.

    Args:
        items: List of StashItem objects or raw dictionary payloads.

    Returns:
        List of aggregated ParentYarnGroup objects.
    """
    if not items:
        return []

    validated_items: list[StashItem] = [
        item if isinstance(item, StashItem) else StashItem.model_validate(item)
        for item in items
    ]

    groups_map: dict[tuple[str, str], list[StashItem]] = {}
    for item in validated_items:
        brand, yarn = _resolve_brand_and_yarn(item)
        key = (brand, yarn)
        if key not in groups_map:
            groups_map[key] = []
        groups_map[key].append(item)

    groups: list[ParentYarnGroup] = []
    for (brand, yarn), group_items in groups_map.items():
        total_skeins = 0.0
        total_yards = 0.0
        total_meters = 0.0
        total_grams = 0.0
        photo_url: str | None = None
        latest_date = ""

        for item in group_items:
            # Settle photo
            if not photo_url:
                photo_url = _resolve_photo_url(item)

            # Settle latest date
            item_date = _resolve_item_date(item)
            latest_date = max(latest_date, item_date)

            # Accumulate totals
            if item.skeins is not None:
                total_skeins += float(item.skeins)
                if item.total_yards is not None:
                    total_yards += float(item.total_yards)
                if item.total_meters is not None:
                    total_meters += float(item.total_meters)
                if item.total_grams is not None:
                    total_grams += float(item.total_grams)
            elif item.packs:
                for pack in item.packs:
                    if pack.skeins is not None:
                        total_skeins += pack.skeins
                    if pack.total_yards is not None:
                        total_yards += pack.total_yards
                    if pack.total_meters is not None:
                        total_meters += pack.total_meters
                    if pack.total_grams is not None:
                        total_grams += pack.total_grams
            elif item.primary_pack:
                pack = item.primary_pack
                if pack.skeins is not None:
                    total_skeins += pack.skeins
                if pack.total_yards is not None:
                    total_yards += pack.total_yards
                if pack.total_meters is not None:
                    total_meters += pack.total_meters
                if pack.total_grams is not None:
                    total_grams += pack.total_grams

        display_title = f"{brand} — {yarn}"

        groups.append(
            ParentYarnGroup(
                brand_name=brand,
                yarn_name=yarn,
                display_title=display_title,
                items=group_items,
                total_items=len(group_items),
                total_skeins=round(total_skeins, 2),
                total_yards=round(total_yards, 2),
                total_meters=round(total_meters, 2),
                total_grams=round(total_grams, 2),
                photo_url=photo_url,
                latest_date=latest_date,
                group_key=f"{brand}::{yarn}",
            )
        )

    return groups


def filter_stash_groups(
    groups: list[ParentYarnGroup],
    query: str | None,
) -> list[ParentYarnGroup]:
    """Filter parent yarn groups by brand, yarn name, or child item colorways.

    Args:
        groups: List of ParentYarnGroup objects.
        query: Case-insensitive search query string.

    Returns:
        Filtered list of ParentYarnGroup objects.
    """
    if not query or not query.strip():
        return groups

    q = query.strip().lower()
    filtered: list[ParentYarnGroup] = []

    for group in groups:
        # Check brand name, yarn product name, and display title
        if (
            q in group.brand_name.lower()
            or q in group.yarn_name.lower()
            or q in group.display_title.lower()
        ):
            filtered.append(group)
            continue

        # Check colorways, dye lots, locations, and tag names in child items
        matched = False
        for item in group.items:
            colorway = (item.colorway_name or "").lower()
            dye_lot = (item.dye_lot or "").lower()
            location = (item.location or "").lower()
            name = (item.name or "").lower()
            tags = " ".join(t.lower() for t in item.tag_names)
            packs_cw = " ".join((p.colorway or "").lower() for p in item.packs)

            if (
                q in colorway
                or q in dye_lot
                or q in location
                or q in name
                or q in tags
                or q in packs_cw
            ):
                matched = True
                break

        if matched:
            filtered.append(group)

    return filtered


def sort_stash_groups(
    groups: list[ParentYarnGroup],
    sort_by: str = "brand_asc",
) -> list[ParentYarnGroup]:
    """Sort parent yarn groups by selected order.

    Options:
        - "brand_asc": Alphabetical by Brand name (Default)
        - "name_asc": Alphabetical by Yarn product name
        - "qty_desc": Total skeins in group descending
        - "date_desc": Most recent addition date descending

    Args:
        groups: List of ParentYarnGroup objects.
        sort_by: Sort mode key.

    Returns:
        Sorted list of ParentYarnGroup objects.
    """
    if sort_by == "name_asc":
        return sorted(groups, key=lambda g: (g.yarn_name.lower(), g.brand_name.lower()))
    elif sort_by == "qty_desc":
        return sorted(
            groups,
            key=lambda g: (-g.total_skeins, -g.total_yards, g.brand_name.lower()),
        )
    elif sort_by == "date_desc":
        return sorted(
            groups,
            key=lambda g: (g.latest_date or "", g.brand_name.lower()),
            reverse=True,
        )
    else:  # default "brand_asc"
        return sorted(groups, key=lambda g: (g.brand_name.lower(), g.yarn_name.lower()))


def paginate_stash_groups(
    groups: list[ParentYarnGroup],
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[ParentYarnGroup], int]:
    """Paginate parent yarn groups.

    Args:
        groups: List of ParentYarnGroup objects.
        page: 1-indexed page number.
        page_size: Number of parent yarn groups per page (default 10).

    Returns:
        Tuple of (paginated_groups, total_pages).
    """
    if not groups:
        return [], 1

    total_pages = max(1, math.ceil(len(groups) / page_size))
    current_page = max(1, min(page, total_pages))
    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    return groups[start_idx:end_idx], total_pages


# ---------------------------------------------------------------------------
# UI Components
# ---------------------------------------------------------------------------


def create_stash_item_row(
    item: StashItem | dict[str, Any],
    is_dirty: bool = False,
) -> dbc.ListGroupItem:
    """Render a single colorway stash record row within the expanded parent yarn accordion.

    Args:
        item: StashItem instance or dictionary.
        is_dirty: Whether the item has pending uncommitted local changes.

    Returns:
        dbc.ListGroupItem row component.
    """
    if not isinstance(item, StashItem):
        item = StashItem.model_validate(item)

    colorway_label = item.colorway_name or (
        item.primary_pack.colorway if item.primary_pack and item.primary_pack.colorway else "Default / No Colorway"
    )

    # Status badge formatting
    status_name = item.stash_status.name if item.stash_status else "In stash"
    status_id = item.stash_status.id if item.stash_status else 1

    status_color_map = {
        1: "success",  # In stash
        2: "secondary",  # Used up
        3: "info",  # Will trade/sell / Gifted
        4: "danger",  # Gone / Sold
    }
    status_color = status_color_map.get(status_id, "success")

    # Quantities math
    skeins = 0.0
    yards = 0.0
    grams = 0.0
    if item.skeins is not None:
        skeins = float(item.skeins)
        yards = float(item.total_yards or 0.0)
        grams = float(item.total_grams or 0.0)
    elif item.packs:
        for p in item.packs:
            skeins += p.skeins or 0.0
            yards += p.total_yards or 0.0
            grams += p.total_grams or 0.0
    elif item.primary_pack:
        skeins = item.primary_pack.skeins or 0.0
        yards = item.primary_pack.total_yards or 0.0
        grams = item.primary_pack.total_grams or 0.0

    qty_parts = [f"{skeins:g} sk"]
    sub_parts = []
    if yards > 0:
        sub_parts.append(f"{yards:g} yds")
    if grams > 0:
        sub_parts.append(f"{grams:g} g")

    if sub_parts:
        qty_str = f"{qty_parts[0]} ({' / '.join(sub_parts)})"
    else:
        qty_str = qty_parts[0]

    # Meta badges / info chips
    chips: list[html.Component] = [
        html.Span(f"Colorway: {colorway_label}", className="fw-bold text-light me-2"),
    ]

    dye_lot = item.dye_lot or (item.primary_pack.dye_lot if item.primary_pack else None)
    if dye_lot:
        chips.append(
            dbc.Badge(f"Lot: {dye_lot}", color="dark", className="border border-secondary me-2 text-light", pill=True)
        )

    if item.location:
        chips.append(
            html.Small(f"Loc: {item.location}", className="text-info me-2 fw-semibold")
        )

    chips.append(
        dbc.Badge(
            status_name,
            color=status_color,
            pill=True,
            className="me-2",
            id={"type": "stash-status-badge", "index": item.id},
        )
    )

    if is_dirty:
        chips.append(
            dbc.Badge("Pending Sync", color="warning", pill=True, className="me-2")
        )

    left_content = html.Div(chips, className="d-flex flex-wrap align-items-center mb-1")

    # Extra notes or tags row if present
    notes_row: list[html.Component] = []
    if item.tag_names:
        tags_str = ", ".join(item.tag_names)
        notes_row.append(
            html.Div(
                f"Tags: {tags_str}",
                className="text-muted fst-italic small border-start border-2 border-secondary ps-2 mt-1",
            )
        )

    left_wrapper = html.Div(
        [
            left_content,
            *notes_row,
        ],
        className="me-auto",
    )

    # Right side: Quantity readout + Edit button
    right_wrapper = html.Div(
        [
            html.Span(qty_str, className="fw-semibold text-light me-3 align-self-center"),
            dbc.Button(
                "Edit",
                id={"type": "stash-edit-btn", "index": item.id},
                color="primary",
                outline=True,
                size="sm",
                className="px-3",
            ),
        ],
        className="d-flex align-items-center ms-auto mt-2 mt-md-0",
    )

    return dbc.ListGroupItem(
        dbc.Row(
            [
                dbc.Col(left_wrapper, xs=12, md=8, className="d-flex align-items-center"),
                dbc.Col(right_wrapper, xs=12, md=4, className="d-flex justify-content-md-end align-items-center"),
            ],
            className="align-items-center g-2",
        ),
        className="bg-dark text-light border-secondary py-2 px-3",
    )


def create_parent_yarn_accordion_item(
    group: ParentYarnGroup,
    index: int = 0,
) -> dbc.AccordionItem:
    """Create a single accordion card item for a parent yarn group.

    Args:
        group: ParentYarnGroup aggregate data model.
        index: Index used for unique item_id.

    Returns:
        Configured dbc.AccordionItem component.
    """
    # Thumbnail image or fallback icon
    if group.photo_url:
        thumbnail = html.Img(
            src=group.photo_url,
            alt=group.yarn_name,
            style={"width": "35px", "height": "35px", "objectFit": "cover"},
            className="rounded me-2 flex-shrink-0",
        )
    else:
        thumbnail = html.Div(
            html.I(className="bi bi-box-seam text-success"),
            className="d-inline-flex align-items-center justify-content-center bg-secondary rounded me-2 flex-shrink-0",
            style={"width": "35px", "height": "35px"},
        )

    title_text = html.Span(group.display_title, className="fw-bold fs-6 text-light me-auto")

    items_unit = "item" if group.total_items == 1 else "items"
    badge_label = f"{group.total_items} {items_unit} | {group.total_skeins:g} sk | {group.total_yards:g} yds"
    aggregate_badge = dbc.Badge(
        badge_label,
        color="info",
        pill=True,
        className="ms-auto me-2 px-2 py-1 fs-7 align-self-center",
    )

    header_title = html.Div(
        [
            thumbnail,
            title_text,
            aggregate_badge,
        ],
        className="d-flex align-items-center w-100 pe-2",
    )

    item_rows = [create_stash_item_row(item) for item in group.items]
    body = dbc.ListGroup(item_rows, flush=True, className="border-top border-secondary")

    return dbc.AccordionItem(
        title=header_title,
        item_id=f"stash-group-{index}",
        children=body,
        className="mb-2 border border-secondary rounded overflow-hidden",
    )


def create_grouped_stash_accordion(
    groups: list[ParentYarnGroup],
) -> html.Div | dbc.Accordion:
    """Render the full collapsible accordion container for parent yarn groups.

    Args:
        groups: List of ParentYarnGroup objects to render.

    Returns:
        dbc.Accordion component or empty state Alert.
    """
    if not groups:
        return html.Div(
            dbc.Alert(
                [
                    html.I(className="bi bi-info-circle me-2"),
                    "No stash items found matching criteria.",
                ],
                color="info",
                className="text-center my-4",
            ),
            id="stash-empty-state",
        )

    accordion_items = [
        create_parent_yarn_accordion_item(group, index=i)
        for i, group in enumerate(groups)
    ]

    return dbc.Accordion(
        accordion_items,
        id="stash-accordion",
        start_collapsed=True,
        always_open=True,
        className="mt-2",
    )
