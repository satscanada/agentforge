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
