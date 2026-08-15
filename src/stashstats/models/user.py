from pydantic import BaseModel


class UserProfile(BaseModel):
    """User profile data returned by Ravelry identity endpoints."""

    id: int
    """Unique numeric user ID."""

    username: str
    """Ravelry username."""

    photo_url: str | None = None
    """Avatar image URL."""

    large_photo_url: str | None = None
    """High resolution avatar URL."""

    tiny_photo_url: str | None = None
    """Small thumbnail avatar URL."""

    small_photo_url: str | None = None
    """Medium thumbnail avatar URL."""


class CurrentUserResponse(BaseModel):
    """Payload envelope returned by GET /current_user.json."""

    user: UserProfile
    """Authenticated user profile object."""
