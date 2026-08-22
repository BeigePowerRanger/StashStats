from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings and API credentials loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    access_key: str = Field(
        default="",
        validation_alias=AliasChoices("API_USERNAME", "RAVELRY_ACCESS_KEY", "ACCESS_KEY"),
    )
    """Ravelry API Access Key (HTTP Basic Auth username)."""

    personal_key: SecretStr = Field(
        default=SecretStr(""),
        validation_alias=AliasChoices("API_KEY", "RAVELRY_PERSONAL_KEY", "PERSONAL_KEY"),
    )
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
