"""Pydantic models for scaffold request and response payloads."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class AgentType(str, Enum):
    """Supported Google ADK agent types."""

    LLM = "llm"
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    LOOP = "loop"


class SessionBackend(str, Enum):
    """Supported session service backends."""

    MEMORY = "memory"
    POSTGRES = "postgres"


class MCPMode(str, Enum):
    """Supported MCP connection modes."""

    DISABLED = "disabled"
    STDIO = "stdio"
    SSE = "sse"


class ToolDefinition(BaseModel):
    """A tool exposed to an agent."""

    name: str
    description: str
    is_deterministic: bool = False
    parameters_schema: dict[str, Any] = Field(default_factory=dict)


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server connection."""

    name: str
    mode: MCPMode = MCPMode.STDIO
    enabled: bool = True
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)
    url: str | None = None

    @model_validator(mode="after")
    def validate_transport(self) -> MCPServerConfig:
        """Require command for stdio and URL for SSE."""
        if self.mode == MCPMode.STDIO and not self.command:
            msg = "command is required when MCP mode is stdio"
            raise ValueError(msg)
        if self.mode == MCPMode.SSE and not self.url:
            msg = "url is required when MCP mode is sse"
            raise ValueError(msg)
        return self


class AgentDefinition(BaseModel):
    """Recursive definition of an agent in the topology."""

    name: str
    agent_type: AgentType
    instructions: str
    model: str | None = None
    tools: list[ToolDefinition] = Field(default_factory=list)
    sub_agents: list[AgentDefinition] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_shape(self) -> AgentDefinition:
        """Enforce sub-agent requirements for orchestration agents."""
        requires_children = self.agent_type in {
            AgentType.SEQUENTIAL,
            AgentType.PARALLEL,
            AgentType.LOOP,
        }
        if requires_children and not self.sub_agents:
            msg = "orchestrator agents must define at least one sub-agent"
            raise ValueError(msg)
        if self.agent_type == AgentType.LLM and self.sub_agents:
            msg = "llm agents cannot define sub_agents"
            raise ValueError(msg)
        return self


class LiteLLMConfig(BaseModel):
    """LiteLLM configuration for generated projects."""

    api_base: str = "http://127.0.0.1:4000/v1"
    api_key_env: str = "LITELLM_API_KEY"
    model: str = "gemini/gemini-2.0-flash"
    provider: str = "openai"
    max_tokens: int = 1024
    temperature: float = 0.2


class SessionConfig(BaseModel):
    """Session service configuration."""

    backend: SessionBackend = SessionBackend.MEMORY
    db_url: str | None = None
    session_ttl_minutes: int = 60

    @model_validator(mode="after")
    def validate_backend(self) -> SessionConfig:
        """Require a database URL for postgres-backed sessions."""
        if self.backend == SessionBackend.POSTGRES and not self.db_url:
            msg = "db_url is required when session backend is postgres"
            raise ValueError(msg)
        return self


class CallbackConfig(BaseModel):
    """Generated callback hook toggles."""

    before_tool_call: bool = True
    after_tool_call: bool = True
    before_agent_call: bool = True
    after_agent_call: bool = False


class ScaffoldRequest(BaseModel):
    """Request payload for scaffold generation."""

    project_name: str
    description: str
    root_agent: AgentDefinition
    mcp_servers: list[MCPServerConfig] = Field(default_factory=list)
    litellm: LiteLLMConfig = Field(default_factory=LiteLLMConfig)
    session: SessionConfig = Field(default_factory=SessionConfig)
    callbacks: CallbackConfig = Field(default_factory=CallbackConfig)


class GeneratedFile(BaseModel):
    """Rendered file returned to the client."""

    filename: str
    content: str


class ScaffoldResponse(BaseModel):
    """Response payload containing rendered files."""

    files: list[GeneratedFile] = Field(default_factory=list)
    download_token: str | None = None


class TestRunRequest(BaseModel):
    """Request payload for executing a live topology test."""

    config: ScaffoldRequest
    message: str = Field(min_length=1)


class TestRunStep(BaseModel):
    """Single simulated step in the live topology run."""

    agent_name: str
    agent_type: AgentType
    depth: int = 0
    mode: str
    summary: str
    tools_used: list[str] = Field(default_factory=list)
    output: str


class TestRunResponse(BaseModel):
    """Response payload for the simulated live run."""

    status: str = "ok"
    project_name: str
    root_agent: str
    input_message: str
    final_output: str
    steps: list[TestRunStep] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
