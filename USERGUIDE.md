# User Guide

This guide is for someone using AgentForge for the first time.

AgentForge is a visual scaffold generator for Google ADK-style agent projects. You define an
agent topology in the UI, configure supporting infrastructure such as MCP servers and session
storage, then generate a downloadable project bundle containing runnable starter code.

If you want the fastest path to getting the app running, start with [QUICKSTART.md](/Users/sathishkr/aigen/agentforge/QUICKSTART.md). If you want to understand how to use the product well, this guide is the main reference.

## What AgentForge Does

AgentForge helps you create a starter project for a multi-agent system. Instead of manually
assembling scaffolding files, you describe your agent setup in the frontend and let the backend
render a project package for you.

The generated bundle includes:

- `agent.py`: the main agent topology wiring
- `tools.py`: tool stubs and deterministic tool definitions
- `callbacks.py`: agent and tool callback hooks
- `main.py`: a CLI entrypoint
- `api_server.py`: an API wrapper with `/health`, `/run`, and `/stream`
- `requirements.txt`: Python dependencies
- `.env.example`: starter environment variables
- `CLAUDE.md`: project context for AI-assisted work
- `README.md`: generated project usage notes
- `LOAD_CONTEXT.md`: generated topology and implementation context
- `TODO.md`: next-step implementation checklist

## Who This Tool Is For

AgentForge is useful if you:

- want a structured starting point for a Google ADK-style agent project
- need a visual way to define orchestration and sub-agent roles
- want to standardize how new agent projects are bootstrapped
- are experimenting with MCP integrations, session backends, or LiteLLM-backed model settings

It is especially useful for internal platform teams, AI engineering teams, and developers who want a predictable scaffold before building business logic.

## How The Application Is Organized

When you open the frontend, the app is divided into a few major areas.

### Header

The top header contains:

- a small backend health dot
- a `Project Name` field
- `Reset Project`
- `Load CD Ladder`
- `Generate`
- `Download`

What these do:

- The health dot is green when the frontend can reach the backend and red when it cannot.
- `Project Name` controls the name used in the scaffold payload and the topology heading.
- `Reset Project` clears the current working configuration and returns to a blank project shape.
- `Load CD Ladder` restores the seeded CD Ladder example.
- `Generate` sends your current configuration to the backend and renders the generated files.
- `Download` downloads the generated ZIP after a successful generation.

### Topology Panel

The left panel is the topology editor. This is where you define the agent tree.

It shows:

- a topology title based on the project name
- `Preview JSON`
- a lock or unlock button
- the root agent and any nested sub-agents

The topology is locked by default to prevent accidental edits. You must unlock it before changing:

- agent names
- agent types
- agent instructions

The lock icon also provides tooltip guidance about whether editing is enabled.

### Code Viewer

The right panel shows the generated project files. Before generation, it shows a live preview based
on the current state. After generation, it shows the real files returned by the backend.

Use this panel to:

- inspect the scaffold output before downloading
- copy generated file contents
- confirm the project structure looks correct

### Bottom Configuration Tabs

The bottom panel exposes additional project configuration in tabs:

- `MCP Config`
- `Session`
- `Env Config`
- `LiteLLM`

These control infrastructure and runtime details outside the topology tree.

## Prerequisites

Before using the application locally, make sure you have:

- Python 3.12.12 available through `pyenv`
- Node.js 18+ and npm
- Docker Desktop if you want to use the Docker workflow

## How To Start The Application

You can run AgentForge either locally or through Docker.

## Option 1: Run Locally

### Start the backend

```bash
cd /Users/sathishkr/aigen/agentforge
pyenv local 3.12.12

cd backend
python --version
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

The backend should be available at:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

### Start the frontend

Open a second terminal:

```bash
cd /Users/sathishkr/aigen/agentforge/frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

## Option 2: Run With Docker

From the repository root:

```bash
cd /Users/sathishkr/aigen/agentforge
./docker-stack.sh build
./docker-stack.sh start
./docker-stack.sh status
```

Useful Docker commands:

```bash
./docker-stack.sh logs
./docker-stack.sh logs backend
./docker-stack.sh logs frontend
./docker-stack.sh stop
./docker-stack.sh deploy
```

The Docker status output also shows the URLs you should use.

## Verify The Application Is Healthy

Before creating or generating anything, confirm the app is healthy.

### Backend verification

Run:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "agentforge",
  "version": "1.0.0"
}
```

You can also open:

```text
http://127.0.0.1:8000/docs
```

### Frontend verification

Open:

```text
http://127.0.0.1:5173
```

Check that:

- the app loads fully
- the health dot is green
- the topology panel is visible
- the code viewer is visible
- the bottom configuration tabs render correctly

## Core Concepts

Before building a new project, it helps to understand the main concepts in the UI.

### Project Name

This is the top-level name for your scaffold request. It affects:

- the visible topology heading
- the identity of the generated project
- the context included in the output files

Choose a short, stable slug-like name such as:

- `customer-support-agent`
- `fraud-review-orchestrator`
- `loan-underwriting-assistant`

### Root Agent

The root agent is the top-level controller of your multi-agent system. It usually:

- coordinates the overall workflow
- decides which sub-agent runs next
- aggregates outputs
- handles the main user-facing objective

### Sub-Agents

Sub-agents break the overall task into focused responsibilities. Each sub-agent can have:

- a name
- an agent type
- instructions
- tools
- additional nested sub-agents

### Agent Types

The UI supports these agent types:

- `llm`
- `sequential`
- `parallel`
- `loop`

Use them this way:

- `llm`: for agents that primarily reason and respond
- `sequential`: for a fixed step-by-step process
- `parallel`: for branches that can run independently
- `loop`: for iterative workflows or retry/evaluate cycles

### Tools

Tools represent the callable functions available to an agent.

In the current UI, tools are shown inside the topology cards and help describe the responsibilities
of each agent. Some tools are marked as deterministic, which means the generated scaffold treats them
as direct Python calls instead of LLM-mediated operations.

### MCP Servers

MCP settings describe how external tools or services are exposed to the generated agent project.

Current modes include:

- `stdio`
- `sse`
- `disabled`

Use these to define whether the generated scaffold should talk to MCP integrations through a local
command or through a network endpoint.

### Session Backend

Session configuration controls how state is stored:

- `memory`: for simple local development
- `postgres`: for a more durable setup

### LiteLLM Settings

These fields control how the generated scaffold should be configured for model access:

- API base URL
- API key environment variable name
- provider
- model
- max tokens
- temperature

## How To Create A New Agent Project From Scratch

This is the recommended path when you want to design your own project instead of starting from the
CD Ladder example.

### Step 1: Reset the project

Click `Reset Project`.

This gives you a clean starting point with:

- a generic project name
- a root agent placeholder
- no preloaded MCP servers
- default session and LiteLLM settings

After reset, the topology returns to locked mode.

### Step 2: Set the project name

Update the `Project Name` field in the header.

Good examples:

- `new-account-onboarding-agent`
- `claims-routing-assistant`
- `portfolio-rebalancing-coordinator`

The topology heading will update automatically based on this value.

### Step 3: Review the root agent

In the topology panel, click the lock icon to unlock editing.

Then update the root agent:

- name
- agent type
- instructions

Example:

- Name: `OnboardingCoordinator`
- Type: `sequential`
- Instructions: `Coordinate document collection, eligibility checks, account setup, and final confirmation.`

### Step 4: Define the agent shape

Think about the workflow before editing the instructions. A good agent tree usually follows business
responsibilities, not just technical functions.

For example, a claims workflow might break into:

- intake agent
- document validation agent
- policy rules agent
- adjudication agent
- notification agent

Even if the current UI does not yet support full drag-and-drop topology construction, the scaffolding
model assumes you are designing a structured, role-based multi-agent workflow.

### Step 5: Use Preview JSON

Click `Preview JSON` to inspect the live request object that the frontend will send to the backend.

Use this when you want to:

- confirm the topology shape
- verify session settings
- verify MCP server configuration
- inspect LiteLLM values
- sanity-check the full payload before generation

This is especially helpful when working with a more complex project or when debugging a bad output.

### Step 6: Configure MCP if needed

Open the `MCP Config` tab.

From here you can:

- review existing MCP servers
- add MCP servers
- switch modes between `stdio`, `sse`, and `disabled`
- update server settings such as command, URL, arguments, and environment values

Use `Add MCP Server` if your generated project should integrate with external tools or data systems.

### Step 7: Configure session storage

Open the `Session` tab.

Choose:

- `Memory` for simple development use
- `Postgres` when you want a more realistic persistent environment

If you choose `Postgres`, fill in the database URL.

### Step 8: Configure environment and model settings

Open the `Env Config` and `LiteLLM` tabs.

Review:

- API base
- API key environment variable
- provider
- model
- token settings
- temperature

These values influence how the generated scaffold is prepared for runtime use.

### Step 9: Generate the project

Click `Generate`.

The frontend sends your current configuration to the backend `POST /api/generate` endpoint. The backend
renders the scaffold and returns a generated file set plus a download token.

When generation completes:

- the code viewer updates with generated files
- the `Download` button becomes available

### Step 10: Review the generated output

Before downloading, inspect the generated files in the code viewer.

Look for:

- correct agent names
- correct topology-related content
- matching tool names
- expected callback structure
- proper API endpoints
- sensible `README.md`, `LOAD_CONTEXT.md`, and `TODO.md` output

### Step 11: Download the scaffold

Click `Download`.

This downloads a ZIP from the backend using the returned token.

Use this when you are ready to:

- extract the project into a new repository
- start implementing real business logic
- share the generated scaffold with teammates

## Recommended Workflow For New Users

If you are using AgentForge for the first time, this sequence works well:

1. Start the app and verify the backend is healthy.
2. Click `Load CD Ladder` and inspect a complete working example.
3. Open `Preview JSON` to understand the request shape.
4. Generate and review the output.
5. Download the ZIP and inspect the files locally.
6. Return to the app.
7. Click `Reset Project`.
8. Create your own project using the same pattern.

This approach helps you learn the product by comparing a known-good seeded example with your own design.

## How To Read The Generated Files

A quick overview of what each generated file is for:

### `agent.py`

This is the main topology wiring file. It reflects your root agent and sub-agent structure.

### `tools.py`

This contains generated tool stubs. Deterministic tools are flagged so they can be handled as direct Python logic.

### `callbacks.py`

This contains hooks for tool and agent lifecycle behavior such as audit logging and guardrails.

### `main.py`

This is a local execution entrypoint for the generated project.

### `api_server.py`

This provides an API wrapper for the generated project, including health and run-style endpoints.

### `CLAUDE.md`

This is generated context for Claude-style AI development support.

### `LOAD_CONTEXT.md`

This captures the project topology and working context for future assisted sessions.

### `TODO.md`

This provides a structured follow-up implementation checklist for the generated project.

## Common Mistakes And How To Avoid Them

### Forgetting to unlock the topology

If you cannot edit agent fields, check the lock icon in the topology header. The topology starts locked by default.

### Generating while the backend is offline

If the health dot is red, generation will not work correctly. Start or restart the backend first.

### Changing fields but not checking the payload

Use `Preview JSON` when something looks wrong. It is the fastest way to confirm the app state before generation.

### Assuming the scaffold is production-ready business logic

The output is a strong starting structure, not a finished business implementation. You still need to:

- implement real tool logic
- connect real backends
- add tests
- validate runtime behavior

### Forgetting to review the generated project files

Always inspect the code viewer before downloading. It is easier to catch naming or configuration issues there than after extraction.

## Troubleshooting

### The frontend loads but the health dot is red

Check the backend:

```bash
curl http://127.0.0.1:8000/health
```

If that fails:

- restart the backend
- verify the Python environment
- check Docker status if you are using containers

### Swagger or backend docs do not load

Open:

```text
http://127.0.0.1:8000/docs
```

If docs fail, confirm:

- backend is running
- Python is 3.12.12 in your active environment
- dependencies were installed with `python -m pip install -r requirements.txt`

### Download does nothing

The `Download` button is only useful after a successful generation. Generate first, then download.

### Docker is running but the UI does not behave correctly

Run:

```bash
./docker-stack.sh status
./docker-stack.sh logs backend
./docker-stack.sh logs frontend
```

## Using The CD Ladder Seed

The CD Ladder example is the built-in demonstration scenario and the best place to learn how AgentForge works.

It represents a deposit recommendation workflow with a root orchestrator and five specialized sub-agents.

### What the seed includes

Project name:

- `cd-ladder-advisor`

Root agent:

- `CDLadderOrchestrator`

Sub-agents:

- `CustomerProfileAgent`
- `RateResearchAgent`
- `LadderCalculatorAgent`
- `ValidationAgent`
- `NotificationAgent`

Deterministic tools highlighted in the UI:

- `calculate_ladder_splits`
- `check_regulatory_limits`

### How to load the seed

Click `Load CD Ladder` in the header.

This restores the full example configuration and locks the topology again by default.

### How to explore the seed

A good way to learn the seed is:

1. Load the CD Ladder example.
2. Review the topology tree.
3. Use `Preview JSON` to inspect the full request object.
4. Unlock the topology if you want to study and edit agent names, types, or instructions.
5. Open the bottom tabs and inspect MCP, session, and LiteLLM configuration.
6. Click `Generate`.
7. Review the generated code in the code viewer.
8. Click `Download`.

### What to look for in the generated output

After generating the CD Ladder scaffold, confirm that:

- the code viewer contains all expected files
- `agent.py` reflects the CD Ladder topology
- `tools.py` includes the CD-related tool stubs
- deterministic tools are clearly represented
- `callbacks.py` includes the expected hook structure
- `LOAD_CONTEXT.md` reflects the ladder scenario
- `TODO.md` provides follow-up work for implementing the generated project

### Why the CD Ladder seed matters

The seed gives first-time users:

- a complete example instead of a blank screen
- a realistic multi-agent decomposition
- a safe way to understand the generated output before creating their own project

If you are new to AgentForge, the CD Ladder example is the best place to start.
