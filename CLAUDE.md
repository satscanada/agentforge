# AgentForge — Project Context

> This file is auto-loaded by Claude in VS Code and referenced by GitHub Copilot.
> For Copilot, invoke `/loadcontext` to restore session context on demand.

## Project Identity

**Name:** AgentForge
**Tagline:** *Scaffold production-ready Google ADK agents in minutes.*
**Repo:** `agentforge`
**Purpose:** A web-based code generation studio that takes a user-defined agent topology
and bootstraps a production-ready Google ADK project — agents, tools, callbacks, MCP
config, session management, FastAPI serving layer, and all project continuity files.
**Audience:** AI engineers and educators building on Google ADK at a Canadian retail bank.
**Stack:** React 18 + Vite + shadcn/ui + Tailwind CSS (frontend) | FastAPI + Jinja2 + Python 3.11+ (backend)

---

## Repository Layout

```
agentforge/
├── .github/
│   ├── copilot-instructions.md                # Always-on rules (auto-injected)
│   ├── prompts/
│   │   └── loadcontext.prompt.md              # /loadcontext slash command
│   └── instructions/
│       ├── python.instructions.md             # Scoped to **/*.py
│       └── typescript.instructions.md         # Scoped to **/*.ts, **/*.tsx
├── frontend/                                  # React/Vite UI
│   └── src/
│       ├── components/
│       │   ├── topology/                      # Agent topology builder
│       │   ├── mcp/                           # MCP config panel
│       │   ├── session/                       # Session backend panel
│       │   ├── env/                           # Env / LiteLLM config panel
│       │   └── output/                        # Code viewer + download
│       ├── store/                             # Zustand (agentConfig.ts)
│       ├── api/                               # scaffold.ts — all API calls
│       └── types/                             # Shared TypeScript interfaces
├── backend/                                   # FastAPI + Jinja2 generator
│   └── app/
│       ├── main.py                            # FastAPI app + /health
│       ├── routers/generate.py                # POST /api/generate, GET /api/download/{token}
│       ├── models/agent_config.py             # Pydantic models
│       ├── generator/
│       │   ├── engine.py                      # GeneratorEngine — render_all()
│       │   └── templates/                     # Jinja2 *.j2 files
│       └── utils/zip_builder.py
├── CLAUDE.md                                  # This file
├── README.md
├── LOAD_CONTEXT.md
├── TODO.md
└── docker-compose.yml
```

---

## Non-Negotiable Architectural Rules

1. **LiteLLM is the only model gateway.** Never use `google-generativeai`, `openai` SDK,
   or any provider SDK directly. Always `from google.adk.models.lite_llm import LiteLlm`.

2. **Deterministic tools are direct Python calls.** If `tool.is_deterministic == True`,
   call it directly in the orchestrator. NEVER wrap as `FunctionTool` or pass to the LLM.

3. **Audit logging belongs in callbacks only.** Never log inside tool functions.
   All logging via `before_tool_call` / `after_tool_call` in `callbacks.py`.

4. **Every generated project exposes `/health`, `/run`, `/stream`** via `api_server.py`.
   `/health` always returns HTTP 200 — never gated behind auth.

5. **Session service is config-driven.** `InMemorySessionService` for `memory`,
   `DatabaseSessionService(db_url=...)` for `postgres`. Never hardcode.

---

## Service URLs

| Service   | URL                              |
|-----------|----------------------------------|
| Frontend  | http://localhost:5173            |
| Backend   | http://localhost:8000            |
| Health    | http://localhost:8000/health     |
| API Docs  | http://localhost:8000/docs       |

---

## Coding Standards

### Python
- Python 3.11+ — use `list[x]`, `x | None` (not `List`, `Optional`)
- Pydantic v2 — `model_validator(mode="after")` not `@validator`
- Jinja2 `Environment` always uses `StrictUndefined`
- Routers contain no business logic — delegate to engine/service classes
- Every public function: type-annotated signature + one-line docstring

### TypeScript
- Strict mode — no `any`, no `!` without explanatory comment
- All shared types in `frontend/src/types/` — never inline in components
- Zustand store is single source of truth — no prop drilling
- All API calls via `frontend/src/api/` — never call `fetch` directly in components
- shadcn/ui only — no additional component libraries

### Git
- Branches: `feature/<short-description>`
- Commits: `feat:`, `fix:`, `chore:`, `docs:`
- Never commit `.env` — `.env.example` only

---

## Agentic Development Protocol

**AI must work one checkpoint at a time. Update `TODO.md`. Stop. Validate. Wait for PROCEED.**

Session-start prompt:
```
Read CLAUDE.md and TODO.md. Find the next incomplete checkpoint.
Implement only that checkpoint. Update TODO.md to reflect progress. Run validation. Output STOP GATE and wait.
```

Resume: type `PROCEED` or `PROCEED: <checkpoint-name>`

See TODO.md for all 8 checkpoints, their tasks, validation steps, and STOP GATE blocks.

---

## LiteLLM Environment Config (generated projects)

```env
LITELLM_API_BASE=http://127.0.0.1:4000/v1
LITELLM_API_KEY=your-litellm-key
LITELLM_MODEL=gemini/gemini-2.0-flash
LITELLM_PROVIDER=openai
LITELLM_MAX_TOKENS=1024
```

---

## Seed Use Case — CD Ladder Advisor

5-agent `SequentialAgent` pipeline used as the default scaffolded example.

```
CDLadderOrchestrator (SequentialAgent)
├── CustomerProfileAgent    → get_customer_profile, get_account_balances
├── RateResearchAgent       → get_current_cd_rates
├── LadderCalculatorAgent   → 🔒 calculate_ladder_splits     [DETERMINISTIC]
├── ValidationAgent         → validate_recommendation, 🔒 check_regulatory_limits [DETERMINISTIC]
└── NotificationAgent       → format_recommendation_output
```

🔒 = direct Python call in orchestrator, never a FunctionTool, never passed to LLM.
