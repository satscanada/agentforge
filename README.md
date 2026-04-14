# AgentForge

> *Scaffold production-ready Google ADK agents in minutes.*

AgentForge is a web-based code generation studio. Define your agent topology in the UI —
agent types, tools, MCP servers, session backend, callbacks — and download a fully wired,
production-ready Google ADK project as a ZIP.

## What Gets Generated

Every scaffolded project includes:

- `agent.py` — ADK agent wiring (LlmAgent, SequentialAgent, ParallelAgent, LoopAgent)
- `tools.py` — tool stubs with deterministic tools flagged as direct Python calls
- `callbacks.py` — `before_tool_call` / `after_tool_call` audit stubs + guardrail hooks
- `main.py` — CLI runner
- `api_server.py` — FastAPI wrapper with `/health`, `/run`, `/stream`
- `requirements.txt`, `.env.example`
- `CLAUDE.md`, `README.md`, `LOAD_CONTEXT.md`, `TODO.md`

## Stack

| Layer    | Technology                                      |
|----------|-------------------------------------------------|
| Frontend | React 18, Vite, TypeScript, shadcn/ui, Tailwind |
| Backend  | FastAPI, Jinja2, Pydantic v2, Python 3.11+      |
| State    | Zustand                                         |

## Prerequisites

- `pyenv`
- Python 3.11+
- Node.js 18+
- npm 9+

## Setup

### Backend

```bash
pyenv local 3.12.12

cd backend
pyenv version
python --version
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

Optional: if you want an isolated `pyenv-virtualenv` for this repo, create one first:

```bash
pyenv virtualenv 3.12.12 agentforge-3.12.12
pyenv local agentforge-3.12.12
```

If `python3` still resolves to a system interpreter in your shell, use `python` after
`pyenv local ...` or run commands through `pyenv exec`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Verify

```bash
curl http://localhost:8000/health
# → {"status":"ok","service":"agentforge","version":"1.0.0"}
```

Open http://localhost:5173

## Development Protocol

This project uses checkpoint-gated agentic development. See `TODO.md` for the 8
checkpoints, each with automated validation steps and a STOP GATE.

Start an AI session with:
```
Read CLAUDE.md and TODO.md. Find the next incomplete checkpoint.
Implement only that checkpoint. Run validation. Output STOP GATE and wait.
```

## Architecture

```
React UI (localhost:5173)
    │
    │  POST /api/generate  { agent topology JSON }
    ▼
FastAPI (localhost:8000)
    │
    │  GeneratorEngine.render_all()
    ▼
Jinja2 Templates (backend/app/generator/templates/)
    │
    │  11 rendered files
    ▼
ZIP → GET /api/download/{token}
    │
    ▼
Browser download
```

## Copilot / Claude Integration

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Always-on project context for Claude |
| `.github/copilot-instructions.md` | Always-on rules for Copilot |
| `.github/prompts/loadcontext.prompt.md` | `/loadcontext` slash command |

## License

Internal — Canadian retail bank AI engineering team.

# agentforge
