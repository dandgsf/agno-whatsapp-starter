"""
My Agent
--------

Seu agente de IA pessoal. Personalize a persona em `agents/prompts.py`
e os guardrails em `agents/guardrails/security.py`.

Rodar standalone:
    python -m agents.my_agent
"""

from os import getenv

from agno.agent import Agent
from agno.models.openai import OpenAIResponses

from agents.guardrails import ContentSafetyGuardrail, enforce_safe_whatsapp_output
from agents.hooks import prepare_multimodal_input
from agents.prompts import instructions
from db import get_postgres_db

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
agent_db = get_postgres_db()
model_id = getenv("OPENAI_MODEL", "gpt-5-mini")

# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------
my_agent = Agent(
    id="my-agent",
    name="My Agent",
    model=OpenAIResponses(id=model_id),
    db=agent_db,
    instructions=instructions,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
    pre_hooks=[prepare_multimodal_input, ContentSafetyGuardrail()],
    post_hooks=[enforce_safe_whatsapp_output],
)


if __name__ == "__main__":
    my_agent.print_response("Oi! Me conta um pouco sobre você.", stream=True)
