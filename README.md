# agno-whatsapp-starter

Template plug-and-play pra subir **um agente de IA que atende no WhatsApp Meta oficial**, com suporte a texto, áudio, imagem e documentos.

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy?template=https://github.com/dandgsf/agno-whatsapp-starter)

Este repo é o projeto prático do módulo **"Agente de IA no WhatsApp com Agno"** do curso **Engenheiro de Produtos IA** da NoCode StartUp.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Framework de agentes | [Agno](https://docs.agno.com) (Python) |
| Runtime | AgentOS |
| Modelo | OpenAI GPT-4.1 |
| Banco | PostgreSQL + pgvector |
| Canal | WhatsApp Business API (Meta oficial) |
| Deploy | [Railway](https://railway.com) (1 clique) |
| Desenvolvimento | Docker Compose + NGrok |

---

## Quickstart — Local

Pré-requisitos: Docker Desktop, Git, uma chave OpenAI, um app WhatsApp no Meta for Developers.

```bash
# 1. Clone e entre na pasta
git clone https://github.com/dandgsf/agno-whatsapp-starter.git
cd agno-whatsapp-starter

# 2. Copie e preencha o .env
cp .env.example .env
# Edite .env e preencha OPENAI_API_KEY
# (as vars WHATSAPP_* podem ficar como estão até a etapa do WhatsApp)

# 3. Suba os containers
docker compose up -d --build

# 4. Confira a saúde
curl http://localhost:8000/health
# => {"status":"ok","service":"agentos",...}
```

Abra `http://localhost:8000` e converse com o seu agente na UI do AgentOS.

### Conectar o WhatsApp local (NGrok)

Quando quiser testar o WhatsApp rodando no seu PC:

```bash
# Em outro terminal
ngrok http 8000
```

No `.env` preencha todas as `WHATSAPP_*` (ver comentários no `.env.example`) e:

```bash
WHATSAPP_ENABLED=true
```

Reinicie: `docker compose restart agentos-api`.

No Meta for Developers → seu App → **WhatsApp → Configuração**:

- Callback URL: `https://<sua-url-ngrok>.ngrok.app/whatsapp/webhook`
- Verify Token: o mesmo valor de `WHATSAPP_VERIFY_TOKEN` no `.env`
- Clicar **Verificar e salvar**
- Em **Campos do webhook → Gerenciar** → marcar `messages` → **Subscribir**

Manda mensagem do número whitelistado → resposta chega.

---

## Quickstart — Produção (Railway)

Clique no botão **Deploy on Railway** no topo deste README.

A Railway provisiona automaticamente:
- o serviço do app (a partir do `Dockerfile`)
- um PostgreSQL com pgvector

No painel Railway, nas variáveis de ambiente do serviço do app:

- preencha `OPENAI_API_KEY`
- preencha as 4 variáveis `WHATSAPP_*` (só depois que quiser ligar o canal)
- `WAIT_FOR_DB=True`
- `PRINT_ENV_ON_LOAD=False`
- para as vars `DB_*`, use **reference variables** do serviço Postgres:
  ```
  DB_HOST=${{Postgres.PGHOST}}
  DB_PORT=${{Postgres.PGPORT}}
  DB_USER=${{Postgres.PGUSER}}
  DB_PASS=${{Postgres.PGPASSWORD}}
  DB_DATABASE=${{Postgres.PGDATABASE}}
  ```

Gere o domínio público em **Settings → Networking → Generate Domain** (no card do serviço do app, não no card do Postgres).

Aponte o webhook do Meta para `https://<seu-app>.up.railway.app/whatsapp/webhook` e pronto — seu agente atende no WhatsApp **sem depender do seu computador ficar ligado**.

---

## Personalizar o agente

Toda a persona fica em `agents/my_agent.py` na variável `instructions`. Edite, rode `docker compose restart agentos-api` (local) ou faça commit + push (Railway redeploya sozinho) e pronto.

Exemplos do que dá pra fazer ao longo da trilha:
- trocar o prompt base pra outra persona (atendimento, SDR, tutor, etc.)
- trocar o modelo (OpenAI → Claude/Gemini, 1 linha)
- adicionar ferramentas (Google Calendar, CRM, MCP, busca web)
- ligar knowledge base (RAG) via UI do `os.agno.com`

---

## Estrutura

```
agno-whatsapp-starter/
├── agents/
│   └── my_agent.py        ← sua persona mora aqui
├── app/
│   ├── main.py            ← ponto de entrada do AgentOS
│   ├── interfaces.py      ← habilita WhatsApp condicionalmente
│   └── config.yaml        ← quick prompts da UI
├── db/                    ← helpers Postgres/pgvector
├── scripts/               ← utilitários de build, deploy, lint
├── tests/                 ← smoke tests
├── compose.yaml           ← dev local (app + pgvector)
├── Dockerfile
├── railway.json           ← config de deploy Railway
└── .env.example
```

---

## Troubleshooting rápido

| Sintoma | Fix |
|---|---|
| `/health` não responde | Aguardar 30-60s no primeiro boot (pgvector subindo) |
| Handshake Meta retorna 403 | `WHATSAPP_VERIFY_TOKEN` do `.env` e do Meta precisam ser **idênticos** |
| `TypeError` no Whatsapp() | Agno 2.5+ lê env vars direto. Não passe kwargs no construtor |
| WhatsApp sem resposta, webhook OK | Meta → Configuração → **Campos de webhook → Gerenciar** → marcar `messages` → **Subscribir** |
| Token WhatsApp expirou | Usou o temporário de 24h. Gerar permanente via System User em `business.facebook.com` |
| Railway não mostra Networking | Você clicou no card do Postgres. Clique no card do app |

---

## Links

- [Agno Docs](https://docs.agno.com)
- [AgentOS](https://docs.agno.com/agent-os/introduction)
- [WhatsApp Interface](https://docs.agno.com/agent-os/interfaces/whatsapp/introduction)
- [Railway deploy](https://docs.agno.com/deploy/templates/railway/deploy)

## Licença

MIT
