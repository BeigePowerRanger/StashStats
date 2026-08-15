from typing import Any, Optional


class RavelryAPIError(Exception):
    """Base exception for all Ravelry API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[Any] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class RavelryAuthError(RavelryAPIError):
    """401 Unauthorized or 403 Forbidden."""


class RavelryNotFoundError(RavelryAPIError):
    """404 Not Found."""


class RavelryRateLimitError(RavelryAPIError):
    """429 Too Many Requests."""


class RavelryServerError(RavelryAPIError):
    """5xx Server errors."""


def raise_for_status_code(
    status_code: int,
    message: str,
    response_body: Optional[Any] = None,
) -> None:
    """Map an HTTP status code to the appropriate exception."""
    if status_code in (401, 403):
        raise RavelryAuthError(message, status_code=status_code, response_body=response_body)
    elif status_code == 404:
        raise RavelryNotFoundError(message, status_code=status_code, response_body=response_body)
    elif status_code == 429:
        raise RavelryRateLimitError(message, status_code=status_code, response_body=response_body)
    elif status_code >= 500:
        raise RavelryServerError(message, status_code=status_code, response_body=response_body)
    elif status_code >= 400:
        raise RavelryAPIError(message, status_code=status_code, response_body=response_body)
