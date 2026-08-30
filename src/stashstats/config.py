from pydantic import AliasChoices, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings and API credentials loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    dev_username: str = Field(
        default="",
        validation_alias=AliasChoices("DEV_USERNAME", "API_USERNAME", "RAVELRY_ACCESS_KEY"),
    )
    """Ravelry Dev Access Key (HTTP Basic Auth username)."""

    dev_api_key: SecretStr = Field(
        default=SecretStr(""),
        validation_alias=AliasChoices("DEV_API_KEY", "API_KEY", "RAVELRY_PERSONAL_KEY"),
    )
    """Ravelry Dev Personal Key (HTTP Basic Auth password)."""

    prod_username: str = Field(
        default="",
        validation_alias="PROD_USERNAME",
    )
    """Ravelry Prod Access Key (HTTP Basic Auth username)."""

    prod_api_key: SecretStr = Field(
        default=SecretStr(""),
        validation_alias="PROD_API_KEY",
    )
    """Ravelry Prod Personal Key (HTTP Basic Auth password)."""

    access_key: str = Field(
        default="",
        validation_alias=AliasChoices("API_USERNAME", "RAVELRY_ACCESS_KEY", "ACCESS_KEY", "DEV_USERNAME", "PROD_USERNAME"),
    )
    """Ravelry API Access Key (HTTP Basic Auth username)."""

    personal_key: SecretStr = Field(
        default=SecretStr(""),
        validation_alias=AliasChoices("API_KEY", "RAVELRY_PERSONAL_KEY", "PERSONAL_KEY", "DEV_API_KEY", "PROD_API_KEY"),
    )
    """Ravelry Personal Key (HTTP Basic Auth password)."""

    base_url: str = "https://api.ravelry.com"
    """Ravelry API base URL."""

    timeout_seconds: float = Field(default=15.0, gt=0)
    """Default request timeout in seconds."""

    @field_validator("dev_username", "prod_username", "access_key", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str | None) -> str:
        return (v or "").strip()

    @property
    def auth_tuple(self) -> tuple[str, str]:
        """Returns (username, password) for HTTP Basic Auth."""
        u = self.dev_username or self.access_key
        p = self.dev_api_key.get_secret_value() or self.personal_key.get_secret_value()
        return (u, p)

    def auth_tuple_for(self, label: str) -> tuple[str, str]:
        """Return (username, password) auth tuple for specified account label ('dev' or 'prod')."""
        normalized = (label or "").strip().lower()
        if normalized == "dev":
            u = self.dev_username or self.access_key
            p = self.dev_api_key.get_secret_value() or self.personal_key.get_secret_value()
            return (u, p)
        elif normalized == "prod":
            return (self.prod_username.strip(), self.prod_api_key.get_secret_value().strip())
        else:
            raise ValueError(f"Unknown account label: {label!r}")


# Loaded once at startup from .env
settings = Settings()
