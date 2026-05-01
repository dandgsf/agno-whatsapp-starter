"""Interface builders for AgentOS."""

from __future__ import annotations

from os import getenv
from typing import Any

from agno.os.interfaces.base import BaseInterface
from agno.os.interfaces.whatsapp import router as whatsapp_router
from agno.os.interfaces.whatsapp.helpers import send_whatsapp_message_async as _send_whatsapp_message_async
from agno.os.interfaces.whatsapp import Whatsapp

_TRUTHY_VALUES = {"1", "true", "yes", "on"}
_PLACEHOLDER_PREFIXES = ("your ",)
_WHATSAPP_REQUIRED_ENV_VARS = (
    "WHATSAPP_ACCESS_TOKEN",
    "WHATSAPP_PHONE_NUMBER_ID",
    "WHATSAPP_VERIFY_TOKEN",
)
_WHATSAPP_CHUNK_DELIMITER = "\n---\n"


def _split_whatsapp_delimited_message(message: str) -> list[str]:
    chunks = [chunk.strip() for chunk in message.split(_WHATSAPP_CHUNK_DELIMITER) if chunk.strip()]
    return chunks if len(chunks) > 1 else [message]


async def _send_chunked_whatsapp_message_async(
    recipient: str, message: Any, config: Any, italics: bool = False
) -> None:
    if isinstance(message, str) and _WHATSAPP_CHUNK_DELIMITER in message:
        for chunk in _split_whatsapp_delimited_message(message):
            await _send_whatsapp_message_async(recipient, chunk, config, italics=italics)
        return

    await _send_whatsapp_message_async(recipient, message, config, italics=italics)


def _patch_whatsapp_chunk_sender() -> None:
    whatsapp_router.send_whatsapp_message_async = _send_chunked_whatsapp_message_async  # type: ignore[assignment]


def _is_enabled(env_var: str) -> bool:
    value = getenv(env_var, "").strip().lower()
    return value in _TRUTHY_VALUES


def _is_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    return not normalized or normalized.startswith(_PLACEHOLDER_PREFIXES)


def _missing_whatsapp_settings() -> list[str]:
    missing: list[str] = []
    for env_var in _WHATSAPP_REQUIRED_ENV_VARS:
        value = getenv(env_var, "")
        if _is_placeholder(value):
            missing.append(env_var)
    if not _is_enabled("WHATSAPP_SKIP_SIGNATURE_VALIDATION") and _is_placeholder(getenv("WHATSAPP_APP_SECRET", "")):
        missing.append("WHATSAPP_APP_SECRET")
    return missing


def build_interfaces(agent: Any) -> list[BaseInterface]:
    """Build external interfaces without enabling networked integrations by accident."""

    if not _is_enabled("WHATSAPP_ENABLED"):
        return []

    missing = _missing_whatsapp_settings()
    if missing:
        missing_vars = ", ".join(missing)
        raise RuntimeError(
            f"WHATSAPP_ENABLED=true but these WhatsApp settings are missing or still placeholders: {missing_vars}"
        )

    _patch_whatsapp_chunk_sender()

    return [
        Whatsapp(
            agent=agent,
        )
    ]
