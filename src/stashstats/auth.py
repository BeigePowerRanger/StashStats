from typing import Any

import httpx
from pydantic import BaseModel

from stashstats.base import BaseAPIClient
from stashstats.config import Settings
from stashstats.config import settings as default_settings
from stashstats.exceptions import RavelryAPIError, RavelryAuthError


class AuthVerificationResult(BaseModel):
    """Structured result of a credential verification check."""

    valid: bool
    """Whether authentication succeeded."""

    username: str | None = None
    """Authenticated Ravelry username."""

    user_id: int | None = None
    """Authenticated Ravelry user ID."""

    photo_url: str | None = None
    """Avatar URL of the authenticated user."""

    status_code: int | None = None
    """HTTP status code returned by the API if failed."""

    error: str | None = None
    """Error message summary if failed."""

    details: Any | None = None
    """Raw response payload or error body."""


class RavelryAuthVerifier(BaseModel):
    """Helper to verify Ravelry API credentials against /current_user.json."""

    settings: Settings = default_settings
    """Application settings containing API credentials."""

    def verify_credentials(self) -> AuthVerificationResult:
        """Calls /current_user.json to verify API keys.

        Returns:
            AuthVerificationResult with valid flag and user details or error info.
        """
        client = BaseAPIClient(settings=self.settings)

        try:
            data = client.get("/current_user.json")
            user = data.get("user", {})
            return AuthVerificationResult(
                valid=True,
                username=user.get("username"),
                user_id=user.get("id"),
                photo_url=user.get("photo_url"),
            )

        except RavelryAuthError as e:
            return AuthVerificationResult(
                valid=False,
                status_code=e.status_code or 401,
                error=str(e),
                details=e.response_body,
            )
        except RavelryAPIError as e:
            return AuthVerificationResult(
                valid=False,
                status_code=e.status_code,
                error=str(e),
                details=e.response_body,
            )
        except httpx.RequestError as e:
            return AuthVerificationResult(
                valid=False,
                error=f"Network error: {e}",
            )
