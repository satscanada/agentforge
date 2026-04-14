# Quickstart

This guide gets AgentForge running quickly and walks through the full CD Ladder
generation flow.

## What You Will Run

- Backend API: `http://localhost:8000`
- Frontend UI: `http://localhost:5173`
- Health check: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

## Option 1: Run Locally

### 1. Start the backend

```bash
cd /Users/sathishkr/aigen/agentforge
pyenv local 3.12.12

cd backend
python --version
python -m pip install -r requirements-dev.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

Expected health response:

```json
{"status":"ok","service":"agentforge","version":"1.0.0"}
```

### 2. Start the frontend

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

## Option 2: Run With Docker

From the repo root:

```bash
cd /Users/sathishkr/aigen/agentforge
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
./docker-stack.sh deploy
```

## Verify The Application

### Backend checks

```bash
curl http://localhost:8000/health
```

Then open:

```text
http://localhost:8000/docs
```

You should see the Swagger UI and the `/health` endpoint.

### Frontend checks

Open:

```text
http://localhost:5173
```

You should see:

- The three-panel layout
- The seeded project name `cd-ladder-advisor`
- The CD Ladder topology with 5 sub-agents
- Lock badges on `calculate_ladder_splits` and `check_regulatory_limits`

## Test The CD Ladder Scenario In The UI

The app is already seeded with the CD Ladder scenario:

- Root agent: `CDLadderOrchestrator`
- Sub-agents:
  - `CustomerProfileAgent`
  - `RateResearchAgent`
  - `LadderCalculatorAgent`
  - `ValidationAgent`
  - `NotificationAgent`

### Generate code from the UI

1. Confirm the backend health indicator is green.
2. Leave the default seeded config in place, or edit the project name if you want.
3. Click `Generate`.
4. Wait for the code viewer to populate.
5. Confirm the viewer shows 11 files:
   - `agent.py`
   - `tools.py`
   - `callbacks.py`
   - `main.py`
   - `api_server.py`
   - `requirements.txt`
   - `.env.example`
   - `CLAUDE.md`
   - `README.md`
   - `LOAD_CONTEXT.md`
   - `TODO.md`
6. Click `Download ZIP`.

### What to verify in generated output

- `agent.py` contains direct calls to:
  - `calculate_ladder_splits()`
  - `check_regulatory_limits()`
- `tools.py` marks deterministic tools with `# DETERMINISTIC`
- `LOAD_CONTEXT.md` lists the CD Ladder topology
- `TODO.md` contains follow-up steps for the generated project

## Test The Backend Directly With The CD Ladder Fixture

You can also test generation without the UI:

```bash
cd /Users/sathishkr/aigen/agentforge/backend

curl -s -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/cd_ladder_config.json
```

To download the ZIP from the response token:

```bash
curl -s -o /tmp/agentforge_output.zip \
  http://localhost:8000/api/download/<download-token>
```

### Run the backend test suite

```bash
cd /Users/sathishkr/aigen/agentforge/backend
python -m pip install -r requirements-dev.txt
python -m pytest tests/test_e2e.py -q
```

## Common Issues

### Backend docs do not load

Make sure the backend is running on Python `3.12.12`:

```bash
python --version
```

### Frontend says backend is offline

Check:

```bash
curl http://localhost:8000/health
```

If that fails, restart the backend or run:

```bash
./docker-stack.sh status
./docker-stack.sh logs backend
```

### Docker stack will not start

Validate the compose setup:

```bash
docker compose config
./docker-stack.sh build
```
