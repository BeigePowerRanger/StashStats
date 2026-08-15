from pydantic import BaseModel


class Paginator(BaseModel):
    """Pagination metadata envelope returned by Ravelry endpoints."""

    page: int
    """Current 1-indexed page number."""

    page_size: int
    """Number of items per page."""

    page_count: int
    """Total number of pages available."""

    last_page: int
    """Index of the last available page."""

    results: int
    """Total count of matching records across all pages."""


class Photo(BaseModel):
    """Image assets and URLs associated with Ravelry entities."""

    id: int
    """Unique photo ID."""

    sort_order: int | None = None
    """Display sort order."""

    user_id: int | None = None
    """Uploader user ID."""

    square_url: str | None = None
    """Square thumbnail image URL."""

    small_url: str | None = None
    """Small thumbnail image URL."""

    medium_url: str | None = None
    """Medium resolution image URL."""

    medium2_url: str | None = None
    """Alternative medium resolution image URL."""

    thumbnail_url: str | None = None
    """Mini thumbnail image URL."""

    small2_url: str | None = None
    """Alternative small image URL."""

    caption: str | None = None
    """Photo caption."""

    copyright_holder: str | None = None
    """Photo copyright owner name."""

    aspect_ratio: float | None = None
    """Image width-to-height ratio."""


class PersonalAttributes(BaseModel):
    """User-specific metadata attached to entities when requested."""

    favorited: bool = False
    """Whether the authenticated user favorited this item."""

    bookmark_id: int | None = None
    """ID of the bookmark if present in user library."""


class YarnCompany(BaseModel):
    """Manufacturer or indie dyer company info."""

    id: int
    """Company numeric database ID."""

    name: str
    """Company name."""

    permalink: str | None = None
    """URL slug for company."""

    url: str | None = None
    """Official company website URL."""

    yarns_count: int | None = None
    """Total number of yarns manufactured."""

