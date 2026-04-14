---
description: 'Load full AgentForge project context for this session'
---

Read `CLAUDE.md` at the project root and `TODO.md`. Treat their contents as active
project context for this session.

Confirm you have loaded both by responding with:

1. **Project name and purpose** (one sentence)
2. **Stack** — frontend and backend
3. **Next checkpoint** — name, goal, and how many tasks remain open
4. **Three most important architectural rules**
5. **Service URLs** — frontend, backend, health

Format:
```
✅ Context loaded — AgentForge
Purpose: ...
Stack: ...
Next checkpoint: CHECKPOINT N — <name> (X tasks remaining)
Key rules:
  1. ...
  2. ...
  3. ...
URLs: Frontend http://localhost:5173 | Backend http://localhost:8000 | Health http://localhost:8000/health
Ready to continue. Type PROCEED to start the next checkpoint.
```
