"""Tests for AgentForge scaffold models."""

from __future__ import annotations

import json
from pathlib import Path

from app.models.agent_config import (
    AgentDefinition,
    AgentType,
    CallbackConfig,
    GeneratedFile,
    LiteLLMConfig,
    MCPMode,
    MCPServerConfig,
    ScaffoldRequest,
    ScaffoldResponse,
    SessionBackend,
    SessionConfig,
    ToolDefinition,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "cd_ladder_config.json"


def test_tool_definition_defaults() -> None:
    """ToolDefinition should default optional fields cleanly."""
    tool = ToolDefinition(name="get_customer_profile", description="Fetch profile data.")

    assert tool.is_deterministic is False
    assert tool.parameters_schema == {}


def test_mcp_server_config_defaults() -> None:
    """MCPServerConfig should default optional fields for stdio servers."""
    server = MCPServerConfig(name="banking-core", command="python")

    assert server.mode == MCPMode.STDIO
    assert server.enabled is True
    assert server.args == []
    assert server.env == {}
    assert server.url is None


def test_recursive_agent_definition_instantiates() -> None:
    """AgentDefinition should support two-level nested sub-agents."""
    nested = AgentDefinition(
        name="TopLevelOrchestrator",
        agent_type=AgentType.SEQUENTIAL,
        instructions="Coordinate the workflow.",
        sub_agents=[
            AgentDefinition(
                name="LoopCoordinator",
                agent_type=AgentType.LOOP,
                instructions="Retry until recommendation is accepted.",
                sub_agents=[
                    AgentDefinition(
                        name="LeafWorker",
                        agent_type=AgentType.LLM,
                        instructions="Handle a single recommendation pass.",
                        model="gemini/gemini-2.0-flash",
                    )
                ],
            )
        ],
    )

    assert nested.sub_agents[0].sub_agents[0].name == "LeafWorker"


def test_litellm_config_defaults() -> None:
    """LiteLLMConfig should expose project default values."""
    config = LiteLLMConfig()

    assert config.api_base == "http://127.0.0.1:4000/v1"
    assert config.api_key_env == "LITELLM_API_KEY"
    assert config.model == "gemini/gemini-2.0-flash"
    assert config.provider == "openai"
    assert config.max_tokens == 1024
    assert config.temperature == 0.2


def test_session_config_defaults() -> None:
    """SessionConfig should default to in-memory sessions."""
    session = SessionConfig()

    assert session.backend == SessionBackend.MEMORY
    assert session.db_url is None
    assert session.session_ttl_minutes == 60


def test_callback_config_defaults() -> None:
    """CallbackConfig should default audit hooks on."""
    callbacks = CallbackConfig()

    assert callbacks.before_tool_call is True
    assert callbacks.after_tool_call is True
    assert callbacks.before_agent_call is True
    assert callbacks.after_agent_call is False


def test_scaffold_request_fixture_loads() -> None:
    """ScaffoldRequest should parse the CD ladder fixture successfully."""
    payload = json.loads(FIXTURE_PATH.read_text())
    request = ScaffoldRequest(**payload)

    assert request.project_name == "agentforge-cd-ladder"
    assert request.root_agent.agent_type == AgentType.SEQUENTIAL
    assert len(request.root_agent.sub_agents) == 5
    assert request.litellm.model == "gemini/gemini-2.0-flash"
    assert request.session.backend == SessionBackend.MEMORY
    assert request.callbacks.before_tool_call is True


def test_generated_file_and_response_models() -> None:
    """Response models should accept rendered file payloads."""
    generated_file = GeneratedFile(filename="agent.py", content="print('ok')")
    response = ScaffoldResponse(files=[generated_file], download_token="token-123")

    assert response.files[0].filename == "agent.py"
    assert response.download_token == "token-123"
