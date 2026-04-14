# TODO — AgentForge

> **Protocol:** AI works one checkpoint at a time. After completing a checkpoint it updates
> `TODO.md`, runs automated validation, outputs the STOP GATE block, and halts.
> Resume with: `PROCEED` or `PROCEED: <checkpoint-name>`
>
> **Before starting any checkpoint:** Verify the previous checkpoint is fully complete —
> all tasks marked `[x]`, STOP GATE emitted, and no failing validation steps. If any task
> is incomplete or validation failed, resolve it before proceeding to the next checkpoint.

---

## CHECKPOINT 1 — Project Scaffold & Copilot Context
**Goal:** Bare repo exists, all Copilot/Claude context files in place. Dev can open the
project in VS Code and immediately get correct AI assistance.

### Tasks
- [x] Create repo `agentforge/` with top-level `CLAUDE.md`, `README.md`, `LOAD_CONTEXT.md`, `TODO.md`
- [x] Create `.github/copilot-instructions.md`
- [x] Create `.github/prompts/loadcontext.prompt.md`
- [x] Create `.github/instructions/python.instructions.md`
- [x] Create `.github/instructions/typescript.instructions.md`
- [x] Create `backend/` and `frontend/` directory stubs with placeholder README each
- [x] Create `docker-compose.yml` stub (services defined, not yet functional)

### Validation — AUTOMATED
```bash
test -f CLAUDE.md                                          && echo "PASS: CLAUDE.md"                    || echo "FAIL: CLAUDE.md"
test -f TODO.md                                            && echo "PASS: TODO.md"                      || echo "FAIL: TODO.md"
test -f LOAD_CONTEXT.md                                    && echo "PASS: LOAD_CONTEXT.md"              || echo "FAIL: LOAD_CONTEXT.md"
test -f .github/copilot-instructions.md                    && echo "PASS: copilot-instructions.md"      || echo "FAIL: copilot-instructions.md"
test -f .github/prompts/loadcontext.prompt.md              && echo "PASS: loadcontext.prompt.md"        || echo "FAIL: loadcontext.prompt.md"
test -f .github/instructions/python.instructions.md        && echo "PASS: python.instructions.md"      || echo "FAIL: python.instructions.md"
test -f .github/instructions/typescript.instructions.md    && echo "PASS: typescript.instructions.md"  || echo "FAIL: typescript.instructions.md"
```

### Validation — MANUAL
- [x] Open VS Code, open Copilot Chat, type `/loadcontext` — confirm it appears in the picker
- [x] Ask Copilot: "What are the rules for this project?" — confirm 5 architectural rules returned

### STOP GATE 1
```
✅ CHECKPOINT 1 COMPLETE
Automated: 7/7 PASS
/loadcontext in picker: VERIFIED
Copilot returns 5 rules: VERIFIED
Awaiting: PROCEED
```

---

## CHECKPOINT 2 — Backend: FastAPI Skeleton + Health Check
**Goal:** `uvicorn` starts, `/health` returns 200, `/docs` loads. Nothing else yet.

### Tasks
- [x] `backend/requirements.txt` — fastapi, uvicorn, jinja2, pydantic, python-dotenv
- [x] `backend/.env.example` — placeholder env vars
- [x] `backend/app/__init__.py`
- [x] `backend/app/main.py` — FastAPI app, CORS for `localhost:5173`, `/health` endpoint

### Validation — AUTOMATED
```bash
cd backend
pip install -r requirements.txt -q
uvicorn app.main:app --port 8000 &
sleep 2
curl -s http://localhost:8000/health | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['status'] == 'ok',       f'FAIL: status={d[\"status\"]}'
assert d['service'] == 'agentforge', f'FAIL: service={d[\"service\"]}'
print('PASS: /health')
"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs | grep -q 200 \
  && echo "PASS: /docs" || echo "FAIL: /docs"
kill %1
```

### Validation — MANUAL
- [x] Visit http://localhost:8000/docs — Swagger UI loads, Health tag visible

### STOP GATE 2
```
✅ CHECKPOINT 2 COMPLETE
/health → {"status":"ok","service":"agentforge","version":"1.0.0"}: PASS
/docs loads: PASS
Awaiting: PROCEED
```

---

## CHECKPOINT 3 — Backend: Pydantic Models
**Goal:** All request/response models defined, importable, and tested. No routes yet.

### Tasks
- [x] `backend/app/models/__init__.py`
- [x] `backend/app/models/agent_config.py` — AgentType, SessionBackend, MCPMode,
      ToolDefinition, MCPServerConfig, AgentDefinition (recursive), LiteLLMConfig,
      SessionConfig, CallbackConfig, ScaffoldRequest, GeneratedFile, ScaffoldResponse
- [x] `backend/tests/__init__.py`
- [x] `backend/tests/test_models.py` — instantiate each model with valid data, assert defaults
- [x] `backend/tests/fixtures/cd_ladder_config.json` — CD Ladder seed as JSON payload

### Validation — AUTOMATED
```bash
cd backend
python3 -c "from app.models.agent_config import ScaffoldRequest, ScaffoldResponse; print('PASS: models import')"
python3 -m pytest tests/test_models.py -v
```

### Validation — MANUAL
- [x] `AgentDefinition.sub_agents` is recursive — confirm with a 2-level nested instantiation
- [x] All model fields match UI controls described in CLAUDE.md

### STOP GATE 3
```
✅ CHECKPOINT 3 COMPLETE
Models import: PASS
pytest tests/test_models.py: PASS
Recursive sub_agents: VERIFIED
Awaiting: PROCEED
```

---

## CHECKPOINT 4 — Backend: Jinja2 Engine + Core Templates
**Goal:** Engine renders `agent.py`, `callbacks.py`, `api_server.py` from the CD Ladder
seed config. All three files are syntactically valid Python.

### Tasks
- [x] `backend/app/generator/__init__.py`
- [x] `backend/app/generator/engine.py` — `GeneratorEngine`, `render()`, `render_all()`
- [x] `backend/app/generator/templates/agent.py.j2`
- [x] `backend/app/generator/templates/callbacks.py.j2`
- [x] `backend/app/generator/templates/api_server.py.j2`
- [x] `backend/tests/test_generate.py` — render all 3 templates, assert key identifiers present

### Validation — AUTOMATED
```bash
cd backend
python3 -m pytest tests/test_generate.py -v
python3 -c "
from app.generator.engine import GeneratorEngine
from app.models.agent_config import ScaffoldRequest
import ast, json

with open('tests/fixtures/cd_ladder_config.json') as f:
    config = ScaffoldRequest(**json.load(f))

engine = GeneratorEngine(config)
files = {f.filename: f.content for f in engine.render_all()}

for fname in ['agent.py', 'callbacks.py', 'api_server.py']:
    try:
        ast.parse(files[fname])
        print(f'PASS: {fname} syntax valid')
    except SyntaxError as e:
        print(f'FAIL: {fname} — {e}')
"
```

### Validation — MANUAL
- [x] `agent.py` — `calculate_ladder_splits` and `check_regulatory_limits` appear as **direct calls**, NOT inside `tools=[...]`
- [x] `callbacks.py` — both `audit_before_tool_call` and `guardrail_before_agent` present
- [x] `api_server.py` — `/health`, `/run`, `/stream` all present

### STOP GATE 4
```
✅ CHECKPOINT 4 COMPLETE
pytest tests/test_generate.py: 4 passed, 0 failed
agent.py syntax: VALID
callbacks.py syntax: VALID
api_server.py syntax: VALID
Deterministic tool boundary (manual): VERIFIED
Awaiting: PROCEED
```

---

## CHECKPOINT 5 — Backend: Remaining Templates + ZIP Endpoint
**Goal:** All 11 templates render. `POST /api/generate` returns a downloadable ZIP
containing all 11 files.

### Tasks
- [x] `backend/app/generator/templates/tools.py.j2`
- [x] `backend/app/generator/templates/main.py.j2`
- [x] `backend/app/generator/templates/requirements.txt.j2`
- [x] `backend/app/generator/templates/env.example.j2`
- [x] `backend/app/generator/templates/CLAUDE.md.j2`
- [x] `backend/app/generator/templates/README.md.j2`
- [x] `backend/app/generator/templates/LOAD_CONTEXT.md.j2`
- [x] `backend/app/generator/templates/TODO.md.j2`
- [x] `backend/app/utils/__init__.py`
- [x] `backend/app/utils/zip_builder.py`
- [x] `backend/app/routers/__init__.py`
- [x] `backend/app/routers/generate.py` — `POST /api/generate`, `GET /api/download/{token}`
- [x] Wire router into `main.py`

### Validation — AUTOMATED
```bash
cd backend
uvicorn app.main:app --port 8000 &
sleep 2

RESPONSE=$(curl -s -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/cd_ladder_config.json)

echo $RESPONSE | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert 'files' in d,          'FAIL: no files key'
assert 'download_token' in d, 'FAIL: no download_token'
filenames = [f['filename'] for f in d['files']]
required = ['agent.py','tools.py','callbacks.py','main.py','api_server.py',
            'requirements.txt','.env.example','CLAUDE.md','README.md',
            'LOAD_CONTEXT.md','TODO.md']
for r in required:
    print(f'{'PASS' if r in filenames else 'FAIL'}: {r}')
"

TOKEN=$(echo $RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['download_token'])")
curl -s -o /tmp/agentforge_output.zip http://localhost:8000/api/download/$TOKEN
python3 -c "
import zipfile
with zipfile.ZipFile('/tmp/agentforge_output.zip') as z:
    print('ZIP contents:', z.namelist())
    print('PASS: ZIP valid')
"
kill %1
```

### Validation — MANUAL
- [x] Open `LOAD_CONTEXT.md` from ZIP — agent topology matches CD Ladder seed
- [x] Open `tools.py` — deterministic tools have `# DETERMINISTIC` comment header
- [x] Open `TODO.md` — seeded with next steps relevant to the topology

### STOP GATE 5
```
✅ CHECKPOINT 5 COMPLETE
POST /api/generate: 200 OK
All 11 files in response: PASS
ZIP download: VALID
LOAD_CONTEXT.md content (manual): VERIFIED
Awaiting: PROCEED
```

---

## CHECKPOINT 6 — Frontend: Vite Scaffold + Zustand Store
**Goal:** `npm run dev` starts, app loads at localhost:5173, store initialised with
CD Ladder seed config, TypeScript build is clean.

### Tasks
- [x] `npm create vite@latest frontend -- --template react-ts`
- [x] `npx shadcn@latest init`
- [x] `npm install zustand axios react-syntax-highlighter`
- [x] `npm install -D @types/react-syntax-highlighter`
- [x] `frontend/src/types/index.ts` — all TypeScript interfaces mirroring Pydantic models
- [x] `frontend/src/store/agentConfig.ts` — Zustand store with `DEFAULT_CONFIG` (CD Ladder seed)
- [x] `frontend/src/api/scaffold.ts` — `generateProject()`, `downloadZip()`, `checkHealth()`
- [x] Smoke test: import store in `App.tsx`, render `config.projectName` to screen

### Validation — AUTOMATED
```bash
cd frontend
npm run build 2>&1 | tail -5
# Must exit 0
npx tsc --noEmit && echo "PASS: tsc clean" || echo "FAIL: tsc errors"
```

### Validation — MANUAL
- [x] http://localhost:5173 loads — "cd-ladder-advisor" visible on screen
- [x] Browser console — zero errors

### STOP GATE 6
```
✅ CHECKPOINT 6 COMPLETE
npm run build: EXIT 0
tsc --noEmit: PASS
Store renders projectName: VERIFIED
Awaiting: PROCEED
```

---

## CHECKPOINT 7 — Frontend: Three-Panel Layout + Topology Builder
**Goal:** Layout renders. Topology builder shows CD Ladder agent tree from store.
No API calls yet.

### Tasks
- [x] `frontend/src/App.tsx` — three-panel layout: topology | JSON preview | code viewer
- [x] `frontend/src/components/topology/AgentCard.tsx` — recursive agent + sub-agent renderer
- [x] `frontend/src/components/topology/AgentTypeSelect.tsx` — 4-option shadcn Select
- [x] `frontend/src/components/topology/ToolRow.tsx` — name, description, isDeterministic 🔒 badge + tooltip
- [x] `frontend/src/components/output/CodeViewer.tsx` — tabbed, syntax-highlighted file viewer
- [x] Bottom tab bar: MCP Config | Session | Env Config | LiteLLM (stubs acceptable)
- [x] Header: project name input + Generate button (disabled — not yet wired)

### Validation — AUTOMATED
```bash
cd frontend
npm run build 2>&1 | grep -iE "error" | head -20
npx tsc --noEmit && echo "PASS: tsc clean" || echo "FAIL: tsc errors"
```

### Validation — MANUAL
- [x] 5 sub-agents render correctly in left panel
- [x] `calculate_ladder_splits` shows 🔒 badge
- [x] `check_regulatory_limits` shows 🔒 badge
- [x] JSON preview panel reflects live Zustand state
- [x] Layout usable at 1280px minimum width

### STOP GATE 7
```
✅ CHECKPOINT 7 COMPLETE
tsc --noEmit: PASS
5 sub-agents render: VERIFIED
Lock badges (2 tools): VERIFIED
JSON preview live: VERIFIED
Awaiting: PROCEED
```

---

## CHECKPOINT 8 — Frontend: Full Integration + Download
**Goal:** Generate button calls backend, code viewer populates, ZIP downloads.
Full end-to-end flow works with CD Ladder seed config.

### Tasks
- [x] Wire Generate button → `POST /api/generate` via `frontend/src/api/scaffold.ts`
- [x] On response: populate code viewer tabs from `files[]`
- [x] `frontend/src/components/output/DownloadButton.tsx` — triggers `/api/download/{token}`
- [x] Health indicator in header — polls `/health` every 30s, green/red dot
- [x] MCP Config panel — mode toggle (stdio / sse), conditional fields per mode
- [x] Session panel — radio memory / postgres, conditional DSN field
- [x] LiteLLM panel — all 5 env vars, masked API key input

### Validation — AUTOMATED
```bash
# Backend must be running on port 8000
cd frontend && npm run build && echo "PASS: build clean"
```

### Validation — MANUAL (all 10 must pass)
- [x] Health indicator green when backend running
- [x] Health indicator red when backend stopped
- [x] Generate button shows loading state on click
- [x] Code viewer populates with 11 tabs after generation
- [x] Each tab shows syntax-highlighted code
- [x] Copy button on each tab works
- [x] Download ZIP triggers browser download
- [x] Unzip — all 11 files present
- [x] Edit agent name → JSON preview updates immediately
- [x] Add MCP server (SSE mode) → JSON preview reflects it

### STOP GATE 8
```
✅ CHECKPOINT 8 COMPLETE — MVP DONE
Manual checklist: 10/10 passed
Known issues: Vite chunk-size warning from react-syntax-highlighter bundle
Build: CLEAN
Awaiting: PROCEED (P1) or DONE
```

---

## P1 — Post-MVP (after STOP GATE 8)

- [x] P1-A: `ParallelAgent` and `LoopAgent` in `agent.py.j2`
- [x] P1-B: PostgreSQL session — `DatabaseSessionService` in generated `api_server.py`
- [x] P1-C: `TODO.md.j2` and `CLAUDE.md.j2` fully implemented
- [x] P1-D: `.github/instructions/` files fully implemented
- [x] P1-E: UI — "Add sub-agent" button in topology builder

## V2 — Future (do not implement during MVP sessions)

- [ ] Drag-and-drop canvas (React Flow)
- [x] Live agent test runner
- [ ] GitHub push integration
- [ ] Eval harness generation
- [ ] Java / Spring Boot template set
