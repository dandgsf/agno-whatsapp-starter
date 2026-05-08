"""
Environment validation
----------------------

Validate runtime environment variables before the app bootstraps.
"""

from __future__ import annotations

from functools import lru_cache
from os import getenv

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_PLACEHOLDER_PREFIXES = ("your-", "your ")
_LOCAL_DB_HOSTS = ("", "localhost", "127.0.0.1", "db")


class AppSettings(BaseSettings):
    """Runtime settings loaded from environment variables and `.env`."""

    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"
    openai_audio_transcription_model: str = "gpt-4o-mini-transcribe"
    openai_audio_language: str = "pt"

    database_url: str = ""
    db_host: str = "localhost"
    db_port: str = "5432"
    db_user: str = "ai"
    db_pass: str = "ai"
    db_database: str = "ai"

    whatsapp_enabled: bool = False
    whatsapp_access_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_verify_token: str = ""
    whatsapp_app_secret: str = ""
    whatsapp_skip_signature_validation: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @staticmethod
    def _is_placeholder(value: str) -> bool:
        normalized = value.strip().lower()
        return not normalized or normalized.startswith(_PLACEHOLDER_PREFIXES)

    @staticmethod
    def _is_railway_runtime() -> bool:
        return bool(getenv("RAILWAY_ENVIRONMENT") or getenv("RAILWAY_SERVICE_NAME") or getenv("RAILWAY_PROJECT_ID"))

    @model_validator(mode="after")
    def _validate_required_settings(self) -> "AppSettings":
        if self._is_placeholder(self.openai_api_key):
            raise ValueError(
                "OPENAI_API_KEY is missing or still set to a placeholder value. "
                "On Railway, set it on the application service variables before deploying."
            )

        if self.database_url.strip():
            normalized_db_url = self.database_url.strip().lower()
            if not (
                normalized_db_url.startswith("postgres://")
                or normalized_db_url.startswith("postgresql://")
                or normalized_db_url.startswith("postgresql+psycopg://")
            ):
                raise ValueError("DATABASE_URL must be a Postgres connection URL.")
        elif self._is_railway_runtime() and self.db_host.strip().lower() in _LOCAL_DB_HOSTS:
            raise ValueError(
                "Postgres is not configured for Railway. Set DATABASE_URL=${{Postgres.DATABASE_URL}} "
                "or set DB_HOST, DB_PORT, DB_USER, DB_PASS, and DB_DATABASE from the Postgres service."
            )

        if not self.whatsapp_enabled:
            return self

        missing = []
        if self._is_placeholder(self.whatsapp_access_token):
            missing.append("WHATSAPP_ACCESS_TOKEN")
        if self._is_placeholder(self.whatsapp_phone_number_id):
            missing.append("WHATSAPP_PHONE_NUMBER_ID")
        if self._is_placeholder(self.whatsapp_verify_token):
            missing.append("WHATSAPP_VERIFY_TOKEN")
        if not self.whatsapp_skip_signature_validation and self._is_placeholder(self.whatsapp_app_secret):
            missing.append("WHATSAPP_APP_SECRET")

        if missing:
            missing_vars = ", ".join(missing)
            raise ValueError(
                f"WHATSAPP_ENABLED=true but these settings are missing or still placeholders: {missing_vars}"
            )

        return self


@lru_cache
def validate_envs() -> AppSettings:
    """Validate environment variables once and return typed settings."""

    return AppSettings()
