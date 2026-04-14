---
applyTo: "**/*.py"
---

# Python Coding Standards — AgentForge

- **Python 3.11+** — use `list[x]`, `dict[x, y]`, `x | None` (never `List`, `Dict`, `Optional`)
- **Pydantic v2** — use `model_validator(mode="after")`, never `@validator`
- **Jinja2** — all `Environment` instances must use `StrictUndefined`; fail loud on missing vars
- **FastAPI routers** contain no business logic — delegate to engine/service classes only
- **Every public function** must have a type-annotated signature and a one-line docstring
- **LiteLLM only** — never import `google.generativeai`, `openai`, or provider SDKs directly
- **Deterministic tools** — if `is_deterministic=True`, call directly; never wrap as `FunctionTool`
- **Callbacks** — all tool audit logging in `before_tool_call` / `after_tool_call` only
