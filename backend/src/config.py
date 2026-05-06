"""
RinggitSense Configuration - Environment settings and constants
"""

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # App Info
    APP_NAME: str = "RinggitSense"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"  # noqa: S104
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://ringgitsense:ringgitsense@localhost:5432/ringgitsense"

    # Security
    SECRET_KEY: str = "change-me-in-production-use-strong-random-key"  # noqa: S105

    # Clerk Authentication
    CLERK_DOMAIN: str = "clerk.your-domain.com"  # e.g., "clerk.ringgitsense.com"
    CLERK_JWT_AUDIENCE: str = ""  # Optional: restrict to specific audience

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Claude API (for agents)
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list[str] = ["pdf", "csv"]

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Enforce critical settings in production."""
        if self.ENVIRONMENT == "production":
            if self.DEBUG:
                raise ValueError("DEBUG must be False in production")
            if "change-me" in self.SECRET_KEY or len(self.SECRET_KEY) < 32:
                raise ValueError("SECRET_KEY must be a strong random key (32+ chars) in production")
            if "your-domain" in self.CLERK_DOMAIN:
                raise ValueError("CLERK_DOMAIN must be configured in production")
            if any(o.startswith("http://localhost") for o in self.CORS_ORIGINS):
                raise ValueError("CORS_ORIGINS must not contain localhost in production")
        return self


settings = Settings()
