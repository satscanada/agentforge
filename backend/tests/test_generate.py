"""Tests for generator engine rendering."""

from __future__ import annotations

import json
from pathlib import Path

from app.generator.engine import GeneratorEngine
from app.models.agent_config import ScaffoldRequest


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "cd_ladder_config.json"


def load_config() -> ScaffoldRequest:
    """Load the CD ladder scaffold fixture."""
    return ScaffoldRequest(**json.loads(FIXTURE_PATH.read_text()))


def test_render_all_returns_core_files() -> None:
    """Engine should render the full checkpoint-5 file set."""
    engine = GeneratorEngine(load_config())

    files = {generated_file.filename: generated_file.content for generated_file in engine.render_all()}

    assert set(files) == {
        "agent.py",
        "tools.py",
        "callbacks.py",
        "main.py",
        "api_server.py",
        "requirements.txt",
        ".env.example",
        "CLAUDE.md",
        "README.md",
        "LOAD_CONTEXT.md",
        "TODO.md",
    }


def test_agent_template_contains_expected_identifiers() -> None:
    """Agent template should preserve direct deterministic tool calls."""
    engine = GeneratorEngine(load_config())

    content = engine.render("agent.py.j2", "agent.py").content

    assert "CDLadderOrchestratorDefinition" in content
    assert "CustomerProfileAgentDefinition" in content
    assert "calculate_ladder_splits()" in content
    assert "check_regulatory_limits()" in content
    assert 'tools = ["validate_recommendation"]' in content


def test_callbacks_template_contains_expected_hooks() -> None:
    """Callbacks template should render audit and guardrail hooks."""
    engine = GeneratorEngine(load_config())

    content = engine.render("callbacks.py.j2", "callbacks.py").content

    assert "audit_before_tool_call" in content
    assert "audit_after_tool_call" in content
    assert "guardrail_before_agent" in content


def test_api_server_template_contains_expected_routes() -> None:
    """API server template should render the required routes."""
    engine = GeneratorEngine(load_config())

    content = engine.render("api_server.py.j2", "api_server.py").content

    assert '@app.get("/health"' in content
    assert '@app.post("/run"' in content
    assert '@app.post("/stream"' in content


def test_tools_and_context_templates_contain_expected_content() -> None:
    """Remaining templates should include deterministic markers and topology context."""
    engine = GeneratorEngine(load_config())

    tools_content = engine.render("tools.py.j2", "tools.py").content
    context_content = engine.render("LOAD_CONTEXT.md.j2", "LOAD_CONTEXT.md").content
    todo_content = engine.render("TODO.md.j2", "TODO.md").content

    assert "# DETERMINISTIC" in tools_content
    assert "calculate_ladder_splits" in tools_content
    assert "check_regulatory_limits" in tools_content
    assert "CDLadderOrchestrator" in context_content
    assert "CustomerProfileAgent" in context_content
    assert "Next Steps" in todo_content


def test_agent_template_parallel_agent_import_and_instantiation() -> None:
    """ParallelAgent import and instantiation are rendered when used in topology."""
    from app.models.agent_config import AgentDefinition, AgentType, ToolDefinition

    request = ScaffoldRequest(
        project_name="parallel-test",
        description="Parallel agent test",
        root_agent=AgentDefinition(
            name="ParallelRoot",
            agent_type=AgentType.PARALLEL,
            instructions="Run sub-agents in parallel.",
            sub_agents=[
                AgentDefinition(
                    name="WorkerAlpha",
                    agent_type=AgentType.LLM,
                    instructions="Worker A.",
                    tools=[ToolDefinition(name="fetch_data", description="Fetch data.")],
                ),
                AgentDefinition(
                    name="WorkerBeta",
                    agent_type=AgentType.LLM,
                    instructions="Worker B.",
                ),
            ],
        ),
    )
    engine = GeneratorEngine(request)
    content = engine.render("agent.py.j2", "agent.py").content

    assert "from google.adk.agents import ParallelAgent" in content
    assert "from google.adk.agents import LlmAgent" in content
    assert "parallel_root = ParallelAgent(" in content
    assert "worker_alpha = LlmAgent(" in content
    assert "worker_beta = LlmAgent(" in content
    assert "root_agent = parallel_root" in content
    assert "SequentialAgent" not in content
    assert "LoopAgent" not in content


def test_agent_template_loop_agent_import_and_instantiation() -> None:
    """LoopAgent import and instantiation are rendered when used in topology."""
    from app.models.agent_config import AgentDefinition, AgentType

    request = ScaffoldRequest(
        project_name="loop-test",
        description="Loop agent test",
        root_agent=AgentDefinition(
            name="LoopRoot",
            agent_type=AgentType.LOOP,
            instructions="Repeat until done.",
            sub_agents=[
                AgentDefinition(
                    name="IterAgent",
                    agent_type=AgentType.LLM,
                    instructions="One iteration.",
                ),
            ],
        ),
    )
    engine = GeneratorEngine(request)
    content = engine.render("agent.py.j2", "agent.py").content

    assert "from google.adk.agents import LoopAgent" in content
    assert "from google.adk.agents import LlmAgent" in content
    assert "loop_root = LoopAgent(" in content
    assert "iter_agent = LlmAgent(" in content
    assert "root_agent = loop_root" in content
    assert "ParallelAgent" not in content
    assert "SequentialAgent" not in content


def test_api_server_memory_session_backend() -> None:
    """api_server.py renders InMemorySessionService when session backend is memory."""
    engine = GeneratorEngine(load_config())
    content = engine.render("api_server.py.j2", "api_server.py").content

    assert "from google.adk.sessions import InMemorySessionService" in content
    assert "session_service = InMemorySessionService()" in content
    assert "DatabaseSessionService" not in content
    assert '"session_backend": "memory"' in content


def test_api_server_postgres_session_backend() -> None:
    """api_server.py renders DatabaseSessionService when session backend is postgres."""
    import json
    from pathlib import Path
    from app.models.agent_config import SessionConfig, SessionBackend

    base = ScaffoldRequest(**json.loads(
        (Path(__file__).parent / "fixtures" / "cd_ladder_config.json").read_text()
    ))
    postgres_config = base.model_copy(update={
        "session": SessionConfig(
            backend=SessionBackend.POSTGRES,
            db_url="postgresql+asyncpg://user:pass@localhost:5432/agentdb",
        )
    })
    engine = GeneratorEngine(postgres_config)
    content = engine.render("api_server.py.j2", "api_server.py").content

    assert "from google.adk.sessions import DatabaseSessionService" in content
    assert "DatabaseSessionService(db_url=_DB_URL)" in content
    assert "InMemorySessionService" not in content
    assert '"session_backend": "postgres"' in content
    assert "postgresql+asyncpg://user:pass@localhost:5432/agentdb" in content


def test_todo_template_contains_topology_aware_tasks() -> None:
    """TODO.md renders checkpoint structure with deterministic tool tasks."""
    engine = GeneratorEngine(load_config())
    content = engine.render("TODO.md.j2", "TODO.md").content

    assert "CHECKPOINT 1" in content
    assert "CHECKPOINT 2" in content
    assert "CHECKPOINT 3" in content
    assert "CHECKPOINT 4" in content
    assert "STOP GATE" in content
    assert "calculate_ladder_splits" in content
    assert "check_regulatory_limits" in content
    assert "DETERMINISTIC" in content
    assert "get_customer_profile" in content
    assert "Backlog" in content


def test_todo_template_postgres_section_gated_by_backend() -> None:
    """TODO.md includes DATABASE_URL task only when session backend is postgres."""
    from app.models.agent_config import SessionConfig, SessionBackend

    base = load_config()
    pg_cfg = base.model_copy(update={
        "session": SessionConfig(
            backend=SessionBackend.POSTGRES,
            db_url="postgresql+asyncpg://u:p@localhost/db",
        )
    })
    mem_content = GeneratorEngine(base).render("TODO.md.j2", "TODO.md").content
    pg_content = GeneratorEngine(pg_cfg).render("TODO.md.j2", "TODO.md").content

    assert "DATABASE_URL" in pg_content
    assert "DATABASE_URL" not in mem_content


def test_claude_template_contains_full_topology_and_rules() -> None:
    """CLAUDE.md renders all 5 rules, agent topology, LiteLLM config, and file map."""
    engine = GeneratorEngine(load_config())
    content = engine.render("CLAUDE.md.j2", "CLAUDE.md").content

    assert "Non-Negotiable Architectural Rules" in content
    assert "LiteLLM is the only model gateway" in content
    assert "Deterministic tools are direct Python calls" in content
    assert "Audit logging belongs in callbacks only" in content
    assert "Session service is config-driven" in content
    assert "calculate_ladder_splits" in content
    assert "check_regulatory_limits" in content
    assert "Agent Topology" in content
    assert "CDLadderOrchestrator" in content
    assert "CustomerProfileAgent" in content
    assert "LiteLLM Configuration" in content
    assert "gemini/gemini-2.0-flash" in content
    assert "Service URLs" in content
    assert "File Map" in content
    assert "InMemorySessionService" in content


def test_claude_template_postgres_session_rule() -> None:
    """CLAUDE.md references DatabaseSessionService when backend is postgres."""
    from app.models.agent_config import SessionConfig, SessionBackend

    base = load_config()
    pg_cfg = base.model_copy(update={
        "session": SessionConfig(
            backend=SessionBackend.POSTGRES,
            db_url="postgresql+asyncpg://u:p@localhost/db",
        )
    })
    pg_content = GeneratorEngine(pg_cfg).render("CLAUDE.md.j2", "CLAUDE.md").content
    mem_content = GeneratorEngine(base).render("CLAUDE.md.j2", "CLAUDE.md").content

    assert "DatabaseSessionService" in pg_content
    assert "InMemorySessionService" not in pg_content
    assert "InMemorySessionService" in mem_content

