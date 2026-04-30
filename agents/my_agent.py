"""
My Agent
--------

Seu agente de IA pessoal. Personalize as `instructions` abaixo
pra ele ter a persona que voce quer.

Rodar standalone:
    python -m agents.my_agent
"""

from os import getenv

from agno.agent import Agent
from agno.models.openai import OpenAIResponses

from agents.hooks import prepare_multimodal_input
from db import get_postgres_db

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
agent_db = get_postgres_db()
model_id = getenv("OPENAI_MODEL", "gpt-4o")

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
- Quando receber imagem: analise o que aparece e responda ao pedido do usuario.
- Quando receber documento: resuma ou responda sobre o conteudo enviado.
- Para WhatsApp: use *negrito* (asterisco simples), _italico_,
  URL pura sem colchetes. NAO use **negrito duplo**, ## headings,
  nem [texto](url) markdown.
- Nunca inclua links, URLs, referencias ou citacoes de fontes na resposta.
- Seja didatico e sucinto: explique com clareza, sem redundancia.
- Se a resposta tiver mais de 190 caracteres, quebre em multiplas mensagens
  separadas por uma linha contendo apenas ---
  Cada parte deve ter sentido completo por si mesma.
- Ao receber audios: processe e responda ao conteudo diretamente.
  O audio e transcrito internamente antes de chegar aqui. Nao mencione
  que recebeu um audio, que esta transcrevendo ou qualquer comentario
  sobre a midia recebida, exceto se a transcricao falhar.
"""

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
    pre_hooks=[prepare_multimodal_input],
)


if __name__ == "__main__":
    my_agent.print_response("Oi! Me conta um pouco sobre voce.", stream=True)
