"""Projects domain client mixin for Ravelry API."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from stashstats.models import (
    Project,
    ProjectDetailResponse,
    ProjectListResponse,
)

if TYPE_CHECKING:
    from stashstats.base import BaseAPIClient

logger = logging.getLogger("stashstats.client.projects")


class ProjectClientMixin:
    """Mixin providing project management, listing, detail, and photo endpoints."""

    def list_projects(
        self: BaseAPIClient | Any,
        username: str | None = None,
        *,
        page: int = 1,
        page_size: int = 50,
        sort: str = "created_",
        query: str | None = None,
        craft: str | None = None,
        status: str | None = None,
    ) -> ProjectListResponse:
        """Fetch a page of projects for a specified or authenticated user.

        Args:
            username: Optional Ravelry username (defaults to authenticated user).
            page: Result page index (1-indexed).
            page_size: Number of items per page.
            sort: Sort order (e.g. 'created_', 'started_', 'completed_', 'name').
            query: Optional search filter within projects.
            craft: Optional filter for craft type.
            status: Optional filter for project status.

        Returns:
            ProjectListResponse with paginator metadata and list of project records.
        """
        target_username = username or getattr(self, "username", None) or getattr(self, "_cached_username", None)
        if not target_username and hasattr(self, "get_current_user"):
            user_resp = self.get_current_user()
            target_username = user_resp.user.username

        params = {
            "page": page,
            "page_size": page_size,
            "sort": sort,
            "query": query,
            "craft": craft,
            "status": status,
        }
        data = self.get(f"/people/{target_username}/projects/list.json", params=params)
        return ProjectListResponse.model_validate(data)

    get_project_list = list_projects
    get_my_projects = list_projects

    def get_project(
        self: BaseAPIClient | Any,
        project_id: int,
        username: str | None = None,
    ) -> ProjectDetailResponse:
        """Fetch details for a single project record.

        Args:
            project_id: Unique project database ID.
            username: Optional username override (defaults to current user).

        Returns:
            ProjectDetailResponse containing detailed project record and comments.
        """
        target_username = username or getattr(self, "username", None) or getattr(self, "_cached_username", None)
        if not target_username and hasattr(self, "get_current_user"):
            user_resp = self.get_current_user()
            target_username = user_resp.user.username

        data = self.get(f"/projects/{target_username}/{project_id}.json")
        return ProjectDetailResponse.model_validate(data)

    def create_project(
        self: BaseAPIClient | Any,
        project_data: dict[str, Any] | Project | None = None,
        *,
        username: str | None = None,
        **kwargs: Any,
    ) -> ProjectDetailResponse | dict[str, Any]:
        """Create a new project record for a user.

        Args:
            project_data: Project data dict or model.
            username: Optional username override.
            **kwargs: Extra fields for project payload.

        Returns:
            Created ProjectDetailResponse or response dict.
        """
        target_username = username or getattr(self, "username", None) or getattr(self, "_cached_username", None)
        if not target_username and hasattr(self, "get_current_user"):
            user_resp = self.get_current_user()
            target_username = user_resp.user.username

        payload = dict(project_data.model_dump() if hasattr(project_data, "model_dump") else (project_data or {}))
        payload.update(kwargs)
        body = payload if "project" in payload else {"project": payload}
        data = self.post(f"/projects/{target_username}/create.json", json=body)
        if isinstance(data, dict) and "project" in data:
            return ProjectDetailResponse.model_validate(data)
        return data

    def update_project(
        self: BaseAPIClient | Any,
        project_id: int,
        project_data: dict[str, Any] | Project | None = None,
        *,
        username: str | None = None,
        **kwargs: Any,
    ) -> ProjectDetailResponse | dict[str, Any]:
        """Update an existing project record.

        Args:
            project_id: Unique project database ID.
            project_data: Project update fields.
            username: Optional username override.
            **kwargs: Extra fields for update.

        Returns:
            Updated ProjectDetailResponse or response dict.
        """
        target_username = username or getattr(self, "username", None) or getattr(self, "_cached_username", None)
        if not target_username and hasattr(self, "get_current_user"):
            user_resp = self.get_current_user()
            target_username = user_resp.user.username

        payload = dict(project_data.model_dump() if hasattr(project_data, "model_dump") else (project_data or {}))
        payload.update(kwargs)
        body = payload if "project" in payload else {"project": payload}
        data = self.post(f"/projects/{target_username}/{project_id}.json", json=body)
        if isinstance(data, dict) and "project" in data:
            return ProjectDetailResponse.model_validate(data)
        return data

    def delete_project(
        self: BaseAPIClient | Any,
        project_id: int,
        username: str | None = None,
    ) -> dict[str, Any]:
        """Delete a project entry.

        Args:
            project_id: Unique project database ID.
            username: Optional username override.

        Returns:
            API confirmation response.
        """
        target_username = username or getattr(self, "username", None) or getattr(self, "_cached_username", None)
        if not target_username and hasattr(self, "get_current_user"):
            user_resp = self.get_current_user()
            target_username = user_resp.user.username

        return self.delete(f"/projects/{target_username}/{project_id}.json")

    def create_project_photo(
        self: BaseAPIClient | Any,
        project_id: int,
        *,
        image_id: int | None = None,
        source_url: str | None = None,
        username: str | None = None,
    ) -> dict[str, Any]:
        """Add a photo to a project using uploaded image ID or source URL.

        Args:
            project_id: Unique project database ID.
            image_id: Optional uploaded image ID.
            source_url: Optional source image URL.
            username: Optional username override.

        Returns:
            API response with status token.
        """
        target_username = username or getattr(self, "username", None) or getattr(self, "_cached_username", None)
        if not target_username and hasattr(self, "get_current_user"):
            user_resp = self.get_current_user()
            target_username = user_resp.user.username

        payload: dict[str, Any] = {}
        if image_id is not None:
            payload["image_id"] = image_id
        if source_url is not None:
            payload["source_url"] = source_url

        return self.post(f"/projects/{target_username}/{project_id}/create_photo.json", json=payload)
