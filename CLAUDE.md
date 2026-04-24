# CLAUDE.md

Contexto pra Claude Code trabalhar neste repo.

## Projeto

**agno-whatsapp-starter** — template plug-and-play pra criar um agente de IA que atende no WhatsApp Meta oficial. Projeto prático do módulo "Agente de IA no WhatsApp com Agno" do curso Engenheiro de Produtos IA (NoCode StartUp).

**Filosofia:** 1 agente, 1 arquivo, poucas abstrações. O aluno precisa bater o olho no código e entender o que está acontecendo.

## Arquitetura

```
AgentOS (app/main.py)
└── My Agent (agents/my_agent.py)   # persona customizavel pelo aluno
```

Interface WhatsApp (`app/interfaces.py`) é ativada automaticamente quando `WHATSAPP_ENABLED=true` e as 4 credenciais estão preenchidas. Webhook path: `/whatsapp/webhook`.

## Stack

| Camada | Tecnologia |
|---|---|
| Framework | Agno (Python) |
| Runtime | AgentOS |
| Modelo | OpenAI GPT-4.1 (`OpenAIResponses`) |
| DB | PostgreSQL + pgvector |
| Canal | WhatsApp Business API (Meta oficial) via `agno.os.interfaces.whatsapp.Whatsapp` |
| Deploy | Railway (1 clique) |

## Arquivos-chave

| Arquivo | Papel |
|---|---|
| `agents/my_agent.py` | **Persona mora aqui.** Aluno edita `instructions`. |
| `app/main.py` | Ponto de entrada. Registra o agent no AgentOS, expõe `/health`. |
| `app/interfaces.py` | Habilita Whatsapp() condicionalmente. Valida env vars. |
| `app/config.yaml` | Quick prompts da UI do AgentOS. |
| `db/session.py` | `get_postgres_db()` helper. |
| `compose.yaml` | Dev local (app + pgvector). |
| `railway.json` | Config de deploy Railway. |
| `.env.example` | Template comentado das env vars. |

## Convenções

### Padrão do agent

```python
from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from db import get_postgres_db

my_agent = Agent(
    id="my-agent",
    name="My Agent",
    model=OpenAIResponses(id="gpt-4.1"),
    db=get_postgres_db(),
    instructions="...",
    enable_agentic_memory=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
```

### WhatsApp interface

`Whatsapp()` do Agno 2.5+ lê env vars direto. **Não passar** `access_token`, `phone_number_id` etc. como kwargs — quebra com `TypeError`. Só passar `agent=my_agent`.

### Banco

- Sem knowledge base, use `get_postgres_db()` direto.
- Se adicionar KB no futuro, usar helper `create_knowledge(name, table)` do `db/`.

## Comandos

```bash
# Setup local
cp .env.example .env
docker compose up -d --build

# Logs
docker compose logs -f agentos-api

# Restart após editar persona
docker compose restart agentos-api

# Smoke tests
./scripts/venv_setup.sh && source .venv/bin/activate
python -m pytest tests/
```

## Env vars

Ver `.env.example` pra lista comentada. Obrigatórias em produção:

- `OPENAI_API_KEY`
- `DB_*` (na Railway, via reference vars do serviço Postgres)
- `WHATSAPP_ENABLED`, `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_VERIFY_TOKEN`, `WHATSAPP_APP_SECRET` quando ligar o canal
- `PRINT_ENV_ON_LOAD=False` (sempre)

## Adicionar features (trilha de evolução)

Alunos avançados podem estender:

- **Tools:** passar `tools=[...]` no Agent. Ex: `GoogleCalendarTools()`, `SlackTools()`, `MCPTools(url=...)`. Lista completa: https://docs.agno.com/tools/toolkits
- **Outro modelo:** trocar `OpenAIResponses(id="gpt-4.1")` por `Claude(id="claude-sonnet-4-5")` (adicionar dep `anthropic` em `pyproject.toml`).
- **Knowledge base:** via UI do `os.agno.com` (Add URL / Upload File) ou via `create_knowledge()` helper em código.
- **Múltiplos agents:** criar outro arquivo em `agents/` e adicionar em `agents=[my_agent, outro_agent]` no `main.py`.

## Referências Agno

- [docs.agno.com/introduction](https://docs.agno.com/introduction)
- [agent-os/introduction](https://docs.agno.com/agent-os/introduction)
- [interfaces/whatsapp](https://docs.agno.com/agent-os/interfaces/whatsapp/introduction)
- [deploy/templates/railway](https://docs.agno.com/deploy/templates/railway/deploy)
- [docs.agno.com/llms-full.txt](https://docs.agno.com/llms-full.txt) (docs completas em formato LLM-friendly)
