import logging
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


logger = logging.getLogger("stashstats.auth")


class AccountManager:
    """Manages active Ravelry account environment (dev vs prod) and client instances."""

    def __init__(self, settings: Settings | None = None, auto_init: bool = True):
        self.settings = settings or default_settings
        self._active_label: str = "dev"
        self._client: Any | None = None
        if auto_init:
            self._init_client()

    def _init_client(self) -> Any:
        """Create and initialize a RavelryClient for the active account."""
        from stashstats.client.ravelry_client import RavelryClient
        from pydantic import SecretStr

        access_key, personal_key = self.settings.auth_tuple_for(self._active_label)
        account_settings = self.settings.model_copy(
            update={
                "access_key": access_key,
                "personal_key": SecretStr(personal_key),
            }
        )
        self._client = RavelryClient(settings=account_settings)
        return self._client

    def get_active_label(self) -> str:
        """Return currently active account label ('dev' or 'prod')."""
        return self._active_label

    def get_target_label(self) -> str:
        """Return the alternate account label ('prod' if active is 'dev', else 'dev')."""
        return "prod" if self._active_label == "dev" else "dev"

    def get_client(self) -> Any:
        """Get active RavelryClient instance, initializing if needed."""
        if self._client is None:
            self._init_client()
        return self._client

    def get_active_username(self) -> str:
        """Get the authenticated Ravelry display name."""
        client = self.get_client()
        if getattr(client, "_cached_username", None):
            return client._cached_username
        cached = getattr(client, "_cached_username", None)
        if isinstance(cached, str) and cached:
            return cached
        try:
            user_resp = client.get_current_user()
            return user_resp.user.username
        except Exception as e:
            logger.warning(f"Failed to fetch current user username: {e}")
            return self._active_label.upper()

    def switch(self, target_label: str | None = None) -> tuple[str, str]:
        """Switch active account to target_label (or toggle if None).

        Returns:
            Tuple of (new_active_label, resolved_username).
        """
        if target_label is not None:
            norm = target_label.strip().lower()
            if norm not in ("dev", "prod"):
                raise ValueError(f"Unknown account label: {target_label!r}")
            self._active_label = norm
        else:
            self._active_label = "prod" if self._active_label == "dev" else "dev"

        self._init_client()
        username = self.get_active_username()
        logger.info(f"Switched account to {self._active_label.upper()} (@{username})")
        return self._active_label, username


account_manager = AccountManager()

