from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings and API credentials loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="RAVELRY_",
        extra="ignore",
    )

    access_key: str
    """Ravelry API Access Key (HTTP Basic Auth username)."""

    personal_key: SecretStr
    """Ravelry Personal Key (HTTP Basic Auth password)."""

    base_url: str = "https://api.ravelry.com"
    """Ravelry API base URL."""

    timeout_seconds: float = 15.0
    """Default request timeout in seconds."""

    @property
    def auth_tuple(self) -> tuple[str, str]:
        """Returns (username, password) for HTTP Basic Auth."""
        return (self.access_key, self.personal_key.get_secret_value())


# Loaded once at startup from .env
settings = Settings()
