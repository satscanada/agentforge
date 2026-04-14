---
applyTo: "**/*.ts,**/*.tsx"
---

# TypeScript Coding Standards — AgentForge

## Language & Type Safety

- **Strict mode** — `tsconfig.json` has `"strict": true`; never disable it
- No `any` — if you genuinely cannot type something, use `unknown` and narrow it
- No non-null assertions (`!`) unless accompanied by an inline comment explaining why
  it cannot be null at that point: `value! // guaranteed by prior guard above`
- Prefer `interface` for object shapes that may be extended; `type` for unions/aliases
- All shared interfaces live in `frontend/src/types/index.ts` — never define types inline
  in component files or in the store
- Mirror every Pydantic backend model as a TypeScript interface in `types/index.ts`
  with camelCase field names (e.g. `agent_type` → `agentType`)

## State Management (Zustand)

- **`useAgentConfigStore`** is the single source of truth for all scaffold config
- Never use `useState` for data that belongs to the scaffold config — use the store
- `useState` is only acceptable for purely local UI state (e.g. hover, open/close)
- Read state with a selector: `const config = useAgentConfigStore(s => s.config)`
  — never destructure the entire store in a component
- Every mutation must go through a named store action — never call `set()` from a component
- Store actions follow the naming pattern: `verb + Field/Agent/Server`
  (e.g. `updateAgentField`, `setAgentType`, `addSubAgent`, `addMcpServer`)
- Use `updateAgentAtPath(agent, path, updater)` for deep agent-tree mutations

## API Layer

- All backend calls go through `frontend/src/api/scaffold.ts` — never call `fetch`
  or `axios` directly from a component
- The three primary functions: `generateProject()`, `downloadZip()`, `checkHealth()`
- Any new endpoint must be added to `scaffold.ts` first, then consumed from components
- Use `axios` for HTTP calls; handle errors by rethrowing typed errors, not `console.error`

## Component Rules

- **shadcn/ui only** — do not `npm install` other UI component libraries
- Use shadcn primitives (`Button`, `Select`, `Input`, `Textarea`, `Badge`, `Tooltip`) for all UI
- Components are function components with explicit return types: `export function Foo(): JSX.Element`
- Props interfaces are defined inline above the component (not exported unless shared)
- `AgentCard` is recursive — always pass `path={[...path, index]}` and `depth={depth + 1}`
  to child `AgentCard` instances
- The `locked` prop on `AgentCard` disables all inputs — respect it; never render
  mutation controls when `locked=true`

## Topology Builder

- `AgentCard` renders one agent and recursively renders `subAgents`
- `ToolRow` renders one tool with a 🔒 badge when `tool.isDeterministic === true`
- `AgentTypeSelect` uses four options matching `AgentType`: `llm`, `sequential`,
  `parallel`, `loop`
- When adding a sub-agent, the new agent default is:
  ```ts
  { name: 'NewAgent', agentType: 'llm', instructions: '', tools: [], subAgents: [] }
  ```
- An `llm` agent cannot have sub-agents — hide / disable the "Add Sub-Agent" button
  when `agent.agentType === 'llm'`

## File Layout

```
frontend/src/
  types/index.ts          — all shared TypeScript interfaces
  store/agentConfig.ts    — Zustand store + DEFAULT_CONFIG + EMPTY_CONFIG
  api/scaffold.ts         — generateProject(), downloadZip(), checkHealth()
  components/
    topology/             — AgentCard, AgentTypeSelect, ToolRow
    output/               — CodeViewer, DownloadButton
    mcp/                  — MCP config panel
    session/              — session backend panel
    env/                  — LiteLLM env panel
  App.tsx                 — three-panel layout + header
```

## Styling

- Tailwind CSS utility classes for layout and spacing
- Component-specific styles in `App.css` using BEM-like class names
- No inline `style={{}}` objects except for CSS custom properties (`--depth`, etc.)
- Minimum supported viewport width: 1280px
