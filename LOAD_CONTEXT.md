# Load Context — AgentForge

> Quick-reference for humans and AI. For a full session context restore, use `/loadcontext`
> in Copilot Chat, or ask Claude to read `CLAUDE.md`.

## What This Project Is

AgentForge is a code generation web app that bootstraps production-ready Google ADK agent
projects. The user defines an agent topology in a UI; the backend renders it into a
downloadable ZIP containing fully wired Python agents, tools, callbacks, a FastAPI server,
and all project continuity files.

## Services

| Service  | URL                          | Notes                        |
|----------|------------------------------|------------------------------|
| Frontend | http://localhost:5173        | React/Vite — `npm run dev`   |
| Backend  | http://localhost:8000        | FastAPI — `uvicorn` on :8000 |
| Health   | http://localhost:8000/health | Always returns HTTP 200      |
| API Docs | http://localhost:8000/docs   | Swagger UI                   |

## Quick Start

```bash
# Terminal 1 — Backend
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend && npm run dev

# Verify backend
curl http://localhost:8000/health
# → {"status":"ok","service":"agentforge","version":"1.0.0"}
```

## Key Architectural Boundaries

1. **LiteLLM only** — never use provider SDKs directly
2. **Deterministic tools = direct Python calls** — never `FunctionTool`, never seen by LLM
3. **Audit logging in callbacks only** — `before_tool_call` / `after_tool_call` in `callbacks.py`
4. **Generated projects always expose** `/health`, `/run`, `/stream` via `api_server.py`
5. **Session service is config-driven** — `InMemorySessionService` or `DatabaseSessionService`

## Copilot / Claude Context Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Full project context — auto-loaded by Claude, read by Copilot |
| `.github/copilot-instructions.md` | Always-on rules injected into every Copilot request |
| `.github/prompts/loadcontext.prompt.md` | `/loadcontext` — restores session context on demand |
| `.github/instructions/python.instructions.md` | Scoped rules for all `*.py` files |
| `.github/instructions/typescript.instructions.md` | Scoped rules for all `*.ts` / `*.tsx` files |

## Agentic Session Protocol

AI works **one checkpoint at a time** from `TODO.md`. After each checkpoint it updates
`TODO.md`, runs automated validation, outputs a STOP GATE block, and halts.

Start a session:
```
Read CLAUDE.md and TODO.md. Find the next incomplete checkpoint.
Implement only that checkpoint. Update TODO.md to reflect progress. Run validation. Output STOP GATE and wait.
```

Resume: type `PROCEED` or `PROCEED: <checkpoint-name>`

## Seed Use Case — CD Ladder Advisor

```
CDLadderOrchestrator (SequentialAgent)
├── CustomerProfileAgent    → get_customer_profile, get_account_balances
├── RateResearchAgent       → get_current_cd_rates
├── LadderCalculatorAgent   → 🔒 calculate_ladder_splits        [DETERMINISTIC]
├── ValidationAgent         → validate_recommendation
│                           → 🔒 check_regulatory_limits        [DETERMINISTIC]
└── NotificationAgent       → format_recommendation_output
```

🔒 = direct Python call in orchestrator — never a FunctionTool.

## Template Outputs (generated per project)

| File | Purpose |
|------|---------|
| `agent.py` | Agent class definitions and wiring |
| `tools.py` | Tool stubs — implement business logic here |
| `callbacks.py` | Audit + guardrail hooks |
| `main.py` | CLI runner entry point |
| `api_server.py` | FastAPI wrapper — `/health`, `/run`, `/stream` |
| `requirements.txt` | Python dependencies |
| `.env.example` | All env vars with inline comments |
| `CLAUDE.md` | Generated project context |
| `README.md` | Setup and architecture |
| `LOAD_CONTEXT.md` | Session restore reference |
| `TODO.md` | Seeded next steps for generated project |
