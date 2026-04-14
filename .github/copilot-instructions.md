# AgentForge — Copilot Instructions

These rules are injected into every GitHub Copilot Chat request in this workspace.

## Non-Negotiable Architectural Rules

1. **LiteLLM is the only model gateway.** Never use `google-generativeai`, `openai` SDK,
   or any provider SDK directly. Always `from google.adk.models.lite_llm import LiteLlm`.

2. **Deterministic tools are direct Python calls.** If a tool is marked `is_deterministic=True`,
   call it directly in the orchestrator. NEVER wrap as `FunctionTool` or pass to the LLM.

3. **Audit logging belongs in callbacks only.** Never log inside tool functions.
   All logging via `before_tool_call` / `after_tool_call` in `callbacks.py`.

4. **Every generated project exposes `/health`, `/run`, `/stream`** via `api_server.py`.
   `/health` always returns HTTP 200 — never gated behind auth.

5. **Session service is config-driven.** `InMemorySessionService` for `memory`,
   `DatabaseSessionService(db_url=...)` for `postgres`. Never hardcode.

## Agentic Development Protocol

- Work **one checkpoint at a time** from `TODO.md`
- After each checkpoint: update `TODO.md`, run automated validation, output STOP GATE block, halt
- Never proceed past a STOP GATE without explicit `PROCEED` from the developer
- Never speculatively implement tasks from future checkpoints

## Stack

- **Backend:** Python 3.11+, FastAPI, Jinja2, Pydantic v2
- **Frontend:** React 18, Vite, TypeScript strict mode, shadcn/ui, Tailwind CSS, Zustand
- No additional UI component libraries beyond shadcn/ui

## Code Style

- Python: type hints on all functions, `model_validator(mode="after")` not `@validator`
- TypeScript: no `any`, no `!` without comment, all types in `frontend/src/types/`
- Zustand store is single source of truth — no prop drilling
- All API calls via `frontend/src/api/` — never `fetch` directly in components
