"""
AgentOS
-------

Ponto de entrada do AgentOS.

Rodar local:
    python -m app.main
"""

from os import getenv
from pathlib import Path
from typing import Any

from agno.os import AgentOS
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.my_agent import my_agent
from app.interfaces import build_interfaces
from db import get_postgres_db


def _get_cors_allow_origins() -> list[str]:
    return [origin.strip().rstrip("/") for origin in getenv("CORS_ALLOW_ORIGINS", "").split(",") if origin.strip()]


base_app = FastAPI(title="AgentOS")

cors_allow_origins = _get_cors_allow_origins()
if cors_allow_origins:
    base_app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

# ---------------------------------------------------------------------------
# Create AgentOS
# ---------------------------------------------------------------------------
agent_os = AgentOS(
    name="AgentOS",
    tracing=True,
    scheduler=True,
    base_app=base_app,
    db=get_postgres_db(),
    agents=[my_agent],
    interfaces=build_interfaces(my_agent),
    config=str(Path(__file__).parent / "config.yaml"),
)

app = agent_os.get_app()


@base_app.get("/health", tags=["Ops"])
def healthcheck() -> dict[str, Any]:
    """Liveness endpoint para o healthcheck da Railway."""

    return {
        "status": "ok",
        "service": "agentos",
        "runtime_env": getenv("RUNTIME_ENV", "prd"),
    }


if __name__ == "__main__":
    agent_os.serve(
        app="main:app",
        reload=getenv("RUNTIME_ENV", "prd") == "dev",
    )
