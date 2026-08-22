"""Pydantic data models for Ravelry Project and Queue API endpoints."""

from typing import Any
from pydantic import BaseModel, Field, field_validator, model_validator
from stashstats.models.common import Paginator, Photo
from stashstats.models.stash import Pack

class ProjectListResult(BaseModel):
    """Summary project record returned in GET /people/{username}/projects/list.json."""

    id: int
    """Unique project ID."""

    name: str = ""
    """User-given project title."""

    status_name: str | None = None
    """Status description (e.g., 'In progress', 'Finished', 'Hibernating', 'Frogged')."""

    progress: int = 0
    """Completion percentage (0 to 100)."""

    craft_name: str | None = None
    """Craft type name (e.g., 'Crochet', 'Knitting', 'Weaving')."""

    pattern_name: str | None = None
    """Title of associated pattern if linked."""

    started: str | None = None
    """Start date string (YYYY/MM/DD or ISO)."""

    completed: str | None = None
    """Completion date string (YYYY/MM/DD or ISO)."""

    rating: int | None = None
    """User rating for pattern experience."""

    first_photo: Photo | None = None
    """Representative photo for project."""

    tag_names: list[str] = Field(default_factory=list)
    """User-assigned tags."""

    @field_validator("progress", mode="before")
    @classmethod
    def normalize_progress(cls, v: Any) -> int:
        if v is None:
            return 0
        try:
            return int(v)
        except (ValueError, TypeError):
            return 0


class Project(ProjectListResult):
    """Full detailed project record returned in GET /projects/{username}/{id}.json."""

    packs: list[Pack] = Field(default_factory=list)
    """Allocated yarn packs and stash items linked to project."""

    photos: list[Photo] = Field(default_factory=list)
    """All photo assets attached to project."""

    notes: str | None = None
    """User project notes and journal entries."""

    notes_html: str | None = None
    """Formatted HTML notes."""

    made_for: str | None = None
    """Gift recipient or client name."""

    size_name: str | None = None
    """Pattern size worked."""


class ProjectListResponse(BaseModel):
    """Response envelope for GET /people/{username}/projects/list.json."""

    projects: list[ProjectListResult] = Field(default_factory=list)
    """List of projects on the current page."""

    paginator: Paginator
    """Pagination metadata metrics."""


class ProjectDetailResponse(BaseModel):
    """Response envelope for GET /projects/{username}/{id}.json."""

    project: Project
    """Detailed project record."""

    comments: list[dict[str, Any]] = Field(default_factory=list)
    """Comments on this project."""


class QueuedProject(BaseModel):
    """Queued pattern entry returned in GET /people/{username}/queue/list.json."""

    id: int
    """Queued record ID."""

    name: str = ""
    """Pattern or project name."""

    sort_order: int = 0
    """Priority ordering index in queue."""

    pattern_name: str | None = None
    """Associated pattern name."""

    pattern_id: int | None = None
    """Associated pattern ID."""

    notes: str | None = None
    """User planning notes."""


class QueueListResponse(BaseModel):
    """Response envelope for GET /people/{username}/queue/list.json."""

    queued_projects: list[QueuedProject] = Field(default_factory=list)
    """List of queued projects."""

    paginator: Paginator
    """Pagination metadata metrics."""
