# AgentForge

AgentForge is a visual scaffold studio for Google ADK-style agent projects. You define an agent
topology in the UI, configure tools, MCP servers, session storage, and model settings, then
generate a runnable starter project as a ZIP.

It is designed for teams that want a faster, more consistent way to bootstrap multi-agent systems
without hand-assembling the same project wiring every time.

## Why It Exists

AgentForge helps you move quickly from idea to working scaffold:

- model a root agent plus nested sub-agents
- switch between `llm`, `sequential`, `parallel`, and `loop` topologies
- define deterministic and non-deterministic tools
- configure MCP servers through `stdio` or `sse`
- choose memory or Postgres-backed session handling
- preview generated files before downloading
- run a live simulated agent test trace against the current topology

## What You Get

Each generated project includes:

- `agent.py` for ADK agent wiring
- `tools.py` for generated tool stubs
- `callbacks.py` for lifecycle hooks
- `main.py` for local execution
- `api_server.py` with `/health`, `/run`, and `/stream`
- `requirements.txt` and `.env.example`
- `README.md`, `LOAD_CONTEXT.md`, `CLAUDE.md`, and `TODO.md`

## Product Snapshot

Current app capabilities:

- topology editor with nested sub-agents
- live JSON state preview
- generated code preview with syntax highlighting
- ZIP download for generated projects
- live test runner that returns a simulated execution trace
- backend health monitoring in the UI

## Stack

| Layer | Technology |
|------|------|
| Frontend | React, Vite, TypeScript, Zustand |
| UI | shadcn/ui, Base UI, custom CSS |
| Backend | FastAPI, Jinja2, Pydantic v2 |
| Runtime target | Google ADK-style Python scaffolds |

## Repo Guide

- [QUICKSTART.md](/Users/sathishkr/aigen/agentforge/QUICKSTART.md): fastest path to running the app
- [USERGUIDE.md](/Users/sathishkr/aigen/agentforge/USERGUIDE.md): detailed product walkthrough
- [TODO.md](/Users/sathishkr/aigen/agentforge/TODO.md): implementation checkpoints and delivery history
- [CLAUDE.md](/Users/sathishkr/aigen/agentforge/CLAUDE.md): AI collaboration and repo context

## Quick Start

### Backend

```bash
cd /Users/sathishkr/aigen/agentforge
pyenv local 3.12.12

cd backend
python --version
python -m pip install -r requirements-dev.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend

Open a second terminal:

```bash
cd /Users/sathishkr/aigen/agentforge/frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

Verify the backend:

```bash
curl http://localhost:8000/health
```

## Typical Workflow

1. Start the backend and frontend.
2. Use the seeded CD Ladder example or reset to a blank project.
3. Unlock the topology and edit agents, instructions, tools, and infrastructure settings.
4. Use `Preview JSON` to verify the live config.
5. Use `Live Test` to simulate an execution trace against the current topology.
6. Click `Generate` to render the scaffold.
7. Review files in the code viewer.
8. Click `Download` to export the ZIP.

## Architecture

```text
Frontend UI (localhost:5173)
  -> POST /api/generate
  -> POST /api/test-run

FastAPI backend (localhost:8000)
  -> GeneratorEngine renders scaffold files
  -> LiveTestRunner simulates topology execution

Artifacts returned to UI
  -> code preview
  -> live test trace
  -> downloadable ZIP
```

## Backend Tests

```bash
cd /Users/sathishkr/aigen/agentforge/backend
python -m pip install -r requirements-dev.txt
python -m pytest tests/test_e2e.py -q
```

## Docker

From the repo root:

```bash
./docker-stack.sh build
./docker-stack.sh start
./docker-stack.sh status
```

Useful commands:

```bash
./docker-stack.sh logs
./docker-stack.sh logs backend
./docker-stack.sh logs frontend
./docker-stack.sh stop
```

## Notes For AI-Assisted Development

This repo was built with checkpoint-driven delivery. If you are continuing implementation with an
AI coding assistant, start with:

```text
Read CLAUDE.md and TODO.md. Find the next incomplete checkpoint.
Implement only that checkpoint. Run validation. Output STOP GATE and wait.
```
