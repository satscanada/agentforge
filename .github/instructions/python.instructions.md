---
applyTo: "**/*.py"
---

# Python Coding Standards — AgentForge

## Language & Typing

- **Python 3.11+** — use built-in generics: `list[x]`, `dict[x, y]`, `tuple[x, ...]`, `x | None`
  — never import `List`, `Dict`, `Optional`, `Tuple` from `typing`
- All public functions must have fully type-annotated signatures (args + return type)
- Every public function must have a one-line docstring — no multi-line, no `Args:` blocks
- Use `from __future__ import annotations` at the top of every module
- Prefer `x | None` over `Optional[x]`; prefer `X | Y` over `Union[X, Y]`

## Pydantic v2

- Use `model_validator(mode="after")` — never `@validator` or `@root_validator`
- Use `Field(default_factory=...)` for mutable defaults (lists, dicts)
- Models are immutable by default — use `model_copy(update={...})` to derive variants
- Never access `__dict__` or `__fields__` — use `.model_dump()` and `.model_fields`
- Enum fields must subclass both `str` and `Enum`: `class MyEnum(str, Enum)`

## FastAPI

- Routers contain **no business logic** — every handler delegates to an engine/service class
- `/health` must always return HTTP 200 and never require auth
- Use `response_model=` on every route that returns a Pydantic model
- Never `raise HTTPException` from inside service/engine classes — only from routers
- CORS: allow `http://localhost:5173` in development; do not wildcard `*` in production

## Jinja2 Templates

- All `Environment` instances must set `undefined=StrictUndefined` — fail loud on missing vars
- Use `trim_blocks=True, lstrip_blocks=True` on every `Environment`
- Register helper functions via `environment.globals["fn_name"] = fn` in `GeneratorEngine.__init__`
- Register Jinja2 filters via `environment.filters["filter_name"] = fn`
- Never use `{% set %}` to mutate outer-scope variables — use `namespace()` for mutable state

## ADK / LiteLLM Rules (Non-Negotiable)

- **LiteLLM only** — never `import google.generativeai`, `import openai`, or any provider SDK
  Always: `from google.adk.models.lite_llm import LiteLlm`
- **Deterministic tools** — any tool with `is_deterministic=True` must be called directly
  in `agent.py` as a plain Python function call, never wrapped as `FunctionTool` or
  passed in `tools=[...]` to an LlmAgent
- **Callbacks only for audit logging** — never log inside tool functions; use
  `before_tool_call` / `after_tool_call` callbacks in `callbacks.py`
- **Session service is config-driven**:
  - `backend == "memory"` → `InMemorySessionService()`
  - `backend == "postgres"` → `DatabaseSessionService(db_url=os.environ["DATABASE_URL"])`
  - Never hardcode DSNs

## GeneratorEngine Patterns

- `render()` takes `template_name` (filename with `.j2`) and `filename` (output filename)
- `render_all()` returns `list[GeneratedFile]` — one entry per scaffold file
- Helper functions registered in `__init__` are available as globals in all templates
- `flatten_agents(agent)` → depth-first list (root first)
- `reverse_flatten_agents(agent)` → bottom-up list (leaves first) — use for instantiation order
- `collect_agent_types(agent)` → `set[str]` — use for conditional imports in templates

## File & Module Layout

```
backend/app/
  main.py           — FastAPI app + CORS + router registration
  models/           — Pydantic models only, no I/O
  routers/          — Route handlers only, no business logic
  generator/
    engine.py       — GeneratorEngine: render(), render_all(), helpers
    templates/      — Jinja2 *.j2 files
  utils/
    zip_builder.py  — ZipBuilder only
```

## Testing

- All tests in `backend/tests/`; use `pytest` with no custom plugins beyond `anyio`
- Load the CD Ladder fixture via `tests/fixtures/cd_ladder_config.json`
- Test template rendering by asserting on string content — do **not** execute generated code
- Use `ast.parse(content)` to assert generated Python is syntactically valid
- Name tests `test_<template>_<what_it_asserts>`
