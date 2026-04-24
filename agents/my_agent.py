"""
My Agent
--------

Seu agente de IA pessoal. Personalize as `instructions` abaixo
pra ele ter a persona que voce quer.

Rodar standalone:
    python -m agents.my_agent
"""

from agno.agent import Agent
from agno.models.openai import OpenAIResponses

from db import get_postgres_db

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
agent_db = get_postgres_db()

# ---------------------------------------------------------------------------
# Persona
# ---------------------------------------------------------------------------
# Edite esta variavel para customizar a personalidade do seu agente.
instructions = """\
Voce e um assistente pessoal prestativo e direto.

- Responda sempre em PT-BR.
- Use linguagem informal mas profissional.
- Evite jargao tecnico sem explicacao.
- Se nao souber algo, admita em vez de inventar.
- Para WhatsApp: use *negrito* (asterisco simples), _italico_,
  URL pura sem colchetes. NAO use **negrito duplo**, ## headings,
  nem [texto](url) markdown.
"""

# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------
my_agent = Agent(
    id="my-agent",
    name="My Agent",
    model=OpenAIResponses(id="gpt-4.1"),
    db=agent_db,
    instructions=instructions,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)


if __name__ == "__main__":
    my_agent.print_response("Oi! Me conta um pouco sobre voce.", stream=True)
