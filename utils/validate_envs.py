"""
Environment validation
----------------------

Validate runtime environment variables before the app bootstraps.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_PLACEHOLDER_PREFIXES = ("your-", "your ")


class AppSettings(BaseSettings):
    """Runtime settings loaded from environment variables and `.env`."""

    openai_api_key: str
    openai_model: str = "gpt-5-mini"
    openai_audio_transcription_model: str = "gpt-4o-mini-transcribe"
    openai_audio_language: str = "pt"

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

    @model_validator(mode="after")
    def _validate_required_settings(self) -> "AppSettings":
        if self._is_placeholder(self.openai_api_key):
            raise ValueError("OPENAI_API_KEY is missing or still set to a placeholder value.")

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
                "WHATSAPP_ENABLED=true but these settings are missing or still placeholders: "
                f"{missing_vars}"
            )

        return self


@lru_cache
def validate_envs() -> AppSettings:
    """Validate environment variables once and return typed settings."""

    return AppSettings()

