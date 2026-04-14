---
applyTo: "**/*.ts,**/*.tsx"
---

# TypeScript Coding Standards — AgentForge

- **Strict mode** — no `any`, no non-null assertions (`!`) without an explanatory comment
- **Shared types** live in `frontend/src/types/index.ts` — never define inline in components
- **Zustand store** is the single source of truth — never use `useState` for shared data
- **API calls** go through `frontend/src/api/scaffold.ts` — never call `fetch` directly in components
- **shadcn/ui only** — do not introduce other UI component libraries
- **No prop drilling** — read state from Zustand in the component that needs it
- **`generateProject()`**, **`downloadZip()`**, **`checkHealth()`** are the only API surface —
  any new backend calls must be added to `frontend/src/api/scaffold.ts` first
