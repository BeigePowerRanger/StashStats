from typing import Any, Self

import httpx
from pydantic import BaseModel, ConfigDict

from stashstats.config import Settings
from stashstats.config import settings as default_settings
from stashstats.exceptions import raise_for_status_code


class BaseAPIClient(BaseModel):
    """Base synchronous HTTP client for handling requests to the Ravelry API."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
        validate_default=True,
    )

    settings: Settings = default_settings
    """Application settings containing credentials and base URL."""

    user_agent: str = "StashStats/0.1.0"
    """User-Agent string sent with requests."""

    _client: httpx.Client | None = None

    @property
    def base_url(self) -> str:
        """Normalized Ravelry API base URL."""
        return self.settings.base_url.rstrip("/")

    @property
    def auth(self) -> tuple[str, str]:
        """Basic Auth username and password tuple."""
        return self.settings.auth_tuple

    @property
    def default_headers(self) -> dict[str, str]:
        """Standard HTTP request headers."""
        return {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }

    def _get_or_create_client(self) -> httpx.Client:
        """Returns the active httpx client or creates a one-off client."""
        if self._client is not None and not self._client.is_closed:
            return self._client
        return httpx.Client(
            base_url=self.base_url,
            auth=self.auth,
            headers=self.default_headers,
            timeout=self.settings.timeout_seconds,
        )

    def __enter__(self) -> Self:

        if self._client is not None and not self._client.is_closed:
            self._client.close()
        self._client = httpx.Client(
            base_url=self.base_url,
            auth=self.auth,
            headers=self.default_headers,
            timeout=self.settings.timeout_seconds,
        )
        return self

    def __exit__(self, *args: object) -> None:
        if self._client is not None and not self._client.is_closed:
            self._client.close()
            self._client = None

    def _clean_params(self, params: dict[str, Any] | None) -> dict[str, Any] | None:
        """Remove None values from query parameters."""
        if not params:
            return None
        return {k: v for k, v in params.items() if v is not None}

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Validate response status code and decode JSON body."""
        if response.is_error:
            try:
                body = response.json()
            except (ValueError, httpx.DecodingError):
                body = response.text
            raise_for_status_code(
                response.status_code,
                f"API request failed ({response.status_code}): {response.reason_phrase}",
                response_body=body,
            )
        return response.json()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Send an HTTP request and return the JSON response.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            path: Relative API path (e.g., '/current_user.json').
            params: Optional query parameters dictionary.
            json: Optional JSON payload for the request body.
            headers: Optional additional headers to merge.
        """
        cleaned_params = self._clean_params(params)
        client = self._get_or_create_client()

        managed_internally = self._client is None
        try:
            response = client.request(
                method=method,
                url=path,
                params=cleaned_params,
                json=json,
                headers=headers,
            )
            return self._handle_response(response)
        finally:
            if managed_internally and not client.is_closed:
                client.close()

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a GET request against the API."""
        return self.request("GET", path, params=params)

    def post(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
    ) -> dict[str, Any]:
        """Execute a POST request against the API."""
        return self.request("POST", path, params=params, json=json)

    def put(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
    ) -> dict[str, Any]:
        """Execute a PUT request against the API."""
        return self.request("PUT", path, params=params, json=json)

    def delete(self, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a DELETE request against the API."""
        return self.request("DELETE", path, params=params)
