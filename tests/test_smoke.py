"""Smoke tests — valida que imports e inicializacao basica funcionam."""

from __future__ import annotations

import os


def test_my_agent_imports() -> None:
    from agents.my_agent import my_agent

    assert my_agent.id == "my-agent"
    assert my_agent.name == "My Agent"


def test_interfaces_disabled_by_default() -> None:
    # Limpa WHATSAPP_ENABLED pra garantir default.
    os.environ.pop("WHATSAPP_ENABLED", None)

    from app.interfaces import build_interfaces

    class _FakeAgent:
        pass

    assert build_interfaces(_FakeAgent()) == []
