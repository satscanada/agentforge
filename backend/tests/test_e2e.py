"""End-to-end tests — simulate full API flow for each agent type."""

from __future__ import annotations

import ast
import json
import zipfile
from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.agent_config import AgentType

client = TestClient(app)

EXPECTED_FILES = {
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


# ---------------------------------------------------------------------------
# Payloads — one per agent type under test
# ---------------------------------------------------------------------------

SIMPLE_LLM_PAYLOAD = {
    "project_name": "simple-chatbot",
    "description": "A single LLM chatbot agent with two tools.",
    "root_agent": {
        "name": "ChatbotAgent",
        "agent_type": "llm",
        "instructions": "You are a helpful assistant that answers questions.",
        "model": "gemini/gemini-2.0-flash",
        "tools": [
            {
                "name": "search_knowledge_base",
                "description": "Search the internal knowledge base.",
                "is_deterministic": False,
            },
            {
                "name": "format_response",
                "description": "Format the response for the user.",
                "is_deterministic": True,
            },
        ],
    },
    "litellm": {
        "api_base": "http://127.0.0.1:4000/v1",
        "api_key_env": "LITELLM_API_KEY",
        "model": "gemini/gemini-2.0-flash",
        "provider": "openai",
        "max_tokens": 512,
        "temperature": 0.3,
    },
    "session": {"backend": "memory"},
    "callbacks": {
        "before_tool_call": True,
        "after_tool_call": True,
        "before_agent_call": True,
        "after_agent_call": False,
    },
}

SEQUENTIAL_PAYLOAD = {
    "project_name": "data-pipeline",
    "description": "A sequential 3-agent data pipeline.",
    "root_agent": {
        "name": "DataPipelineOrchestrator",
        "agent_type": "sequential",
        "instructions": "Run agents one after another to process data.",
        "sub_agents": [
            {
                "name": "DataIngestionAgent",
                "agent_type": "llm",
                "instructions": "Ingest raw data from the source.",
                "model": "gemini/gemini-2.0-flash",
                "tools": [
                    {
                        "name": "fetch_raw_data",
                        "description": "Fetch data from external API.",
                        "is_deterministic": False,
                    },
                ],
            },
            {
                "name": "DataTransformAgent",
                "agent_type": "llm",
                "instructions": "Transform the ingested data.",
                "tools": [
                    {
                        "name": "normalize_records",
                        "description": "Normalize data records.",
                        "is_deterministic": True,
                    },
                    {
                        "name": "validate_schema",
                        "description": "Validate record schema.",
                        "is_deterministic": True,
                    },
                ],
            },
            {
                "name": "DataOutputAgent",
                "agent_type": "llm",
                "instructions": "Output the transformed data.",
                "tools": [
                    {
                        "name": "write_to_store",
                        "description": "Write records to the data store.",
                        "is_deterministic": False,
                    },
                ],
            },
        ],
    },
    "mcp_servers": [
        {
            "name": "data-api",
            "mode": "sse",
            "url": "http://localhost:9090/mcp",
        },
    ],
    "session": {
        "backend": "postgres",
        "db_url": "postgresql+asyncpg://user:pass@localhost:5432/pipeline_db",
    },
}

LLM_WITH_MCP_PAYLOAD = {
    "project_name": "mcp-enabled-bot",
    "description": "A single LLM agent with MCP stdio server.",
    "root_agent": {
        "name": "MCPBotAgent",
        "agent_type": "llm",
        "instructions": "Use the MCP server tools to answer questions.",
        "model": "gemini/gemini-2.0-flash",
        "tools": [
            {
                "name": "lookup_account",
                "description": "Look up customer account.",
                "is_deterministic": False,
            },
        ],
    },
    "mcp_servers": [
        {
            "name": "account-svc",
            "mode": "stdio",
            "command": "python",
            "args": ["-m", "account_mcp"],
            "env": {"API_ENV": "dev"},
        },
    ],
}


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _generate_and_assert_response(payload: dict) -> dict:
    """POST /api/generate and assert the basic response shape."""
    resp = client.post("/api/generate", json=payload)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    data = resp.json()
    assert "files" in data
    assert "download_token" in data
    assert data["download_token"] is not None

    filenames = {f["filename"] for f in data["files"]}
    assert filenames == EXPECTED_FILES, f"Missing files: {EXPECTED_FILES - filenames}"
    return data


def _download_and_assert_zip(token: str) -> dict[str, str]:
    """GET /api/download/{token} and return extracted file map."""
    resp = client.get(f"/api/download/{token}")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"
    assert "attachment" in resp.headers["content-disposition"]

    zf = zipfile.ZipFile(BytesIO(resp.content))
    assert set(zf.namelist()) == EXPECTED_FILES
    return {name: zf.read(name).decode() for name in zf.namelist()}


def _assert_python_syntax(content: str, filename: str) -> None:
    """Assert the content is valid Python by parsing its AST."""
    try:
        ast.parse(content)
    except SyntaxError as exc:
        pytest.fail(f"{filename} has invalid Python syntax: {exc}")


# ---------------------------------------------------------------------------
# E2E: Simple LLM Agent
# ---------------------------------------------------------------------------

class TestE2ESimpleLlmAgent:
    """Full round-trip: generate → download → validate a single LLM agent."""

    def test_generate_returns_all_files(self) -> None:
        """POST /api/generate returns 11 files and a download token."""
        _generate_and_assert_response(SIMPLE_LLM_PAYLOAD)

    def test_download_zip_valid(self) -> None:
        """Download token returns a valid ZIP with all 11 files."""
        data = _generate_and_assert_response(SIMPLE_LLM_PAYLOAD)
        _download_and_assert_zip(data["download_token"])

    def test_agent_py_structure(self) -> None:
        """agent.py imports LlmAgent only, wires the single root agent."""
        data = _generate_and_assert_response(SIMPLE_LLM_PAYLOAD)
        files = _download_and_assert_zip(data["download_token"])
        agent_py = files["agent.py"]

        _assert_python_syntax(agent_py, "agent.py")

        # LlmAgent import present, no orchestrator imports
        assert "from google.adk.agents import LlmAgent" in agent_py
        assert "SequentialAgent" not in agent_py
        assert "ParallelAgent" not in agent_py
        assert "LoopAgent" not in agent_py

        # Agent instance and root assignment
        assert "chatbot_agent = LlmAgent(" in agent_py
        assert "root_agent = chatbot_agent" in agent_py

        # LiteLLM model
        assert "from google.adk.models.lite_llm import LiteLlm" in agent_py
        assert 'model="gemini/gemini-2.0-flash"' in agent_py

    def test_deterministic_tool_boundary(self) -> None:
        """Deterministic tool is direct-called, not in LLM tools list."""
        data = _generate_and_assert_response(SIMPLE_LLM_PAYLOAD)
        files = _download_and_assert_zip(data["download_token"])
        agent_py = files["agent.py"]

        # format_response is deterministic → direct call
        assert "format_response()" in agent_py
        # search_knowledge_base is NOT deterministic → in tools import
        assert "search_knowledge_base" in agent_py
        # format_response should NOT appear in tools=[...] for the LlmAgent
        assert "tools=[search_knowledge_base]" in agent_py

    def test_tools_py_structure(self) -> None:
        """tools.py contains both tools with correct deterministic markers."""
        data = _generate_and_assert_response(SIMPLE_LLM_PAYLOAD)
        files = _download_and_assert_zip(data["download_token"])
        tools_py = files["tools.py"]

        _assert_python_syntax(tools_py, "tools.py")
        assert "search_knowledge_base" in tools_py
        assert "format_response" in tools_py
        assert "# DETERMINISTIC" in tools_py

    def test_callbacks_py_structure(self) -> None:
        """callbacks.py contains expected audit hooks."""
        data = _generate_and_assert_response(SIMPLE_LLM_PAYLOAD)
        files = _download_and_assert_zip(data["download_token"])
        callbacks_py = files["callbacks.py"]

        _assert_python_syntax(callbacks_py, "callbacks.py")
        assert "audit_before_tool_call" in callbacks_py
        assert "audit_after_tool_call" in callbacks_py
        assert "guardrail_before_agent" in callbacks_py

    def test_api_server_routes_and_session(self) -> None:
        """api_server.py has /health, /run, /stream with memory session."""
        data = _generate_and_assert_response(SIMPLE_LLM_PAYLOAD)
        files = _download_and_assert_zip(data["download_token"])
        api_server = files["api_server.py"]

        _assert_python_syntax(api_server, "api_server.py")
        assert '@app.get("/health"' in api_server
        assert '@app.post("/run"' in api_server
        assert '@app.post("/stream"' in api_server
        assert "InMemorySessionService" in api_server
        assert "DatabaseSessionService" not in api_server

    def test_env_example_contains_litellm_vars(self) -> None:
        """.env.example contains all LiteLLM environment variables."""
        data = _generate_and_assert_response(SIMPLE_LLM_PAYLOAD)
        files = _download_and_assert_zip(data["download_token"])
        env_example = files[".env.example"]

        assert "LITELLM_API_BASE" in env_example
        assert "LITELLM_API_KEY" in env_example
        assert "LITELLM_MODEL" in env_example

    def test_all_python_files_valid_syntax(self) -> None:
        """Every .py file in the ZIP parses without SyntaxError."""
        data = _generate_and_assert_response(SIMPLE_LLM_PAYLOAD)
        files = _download_and_assert_zip(data["download_token"])
        for filename, content in files.items():
            if filename.endswith(".py"):
                _assert_python_syntax(content, filename)

    def test_context_files_reference_project(self) -> None:
        """CLAUDE.md, README.md, LOAD_CONTEXT.md reference the project name."""
        data = _generate_and_assert_response(SIMPLE_LLM_PAYLOAD)
        files = _download_and_assert_zip(data["download_token"])

        assert "simple-chatbot" in files["CLAUDE.md"]
        assert "simple-chatbot" in files["README.md"]
        assert "ChatbotAgent" in files["LOAD_CONTEXT.md"]


# ---------------------------------------------------------------------------
# E2E: Sequential Agent with sub-agents
# ---------------------------------------------------------------------------

class TestE2ESequentialAgent:
    """Full round-trip for a sequential orchestrator with 3 sub-agents."""

    def test_generate_returns_all_files(self) -> None:
        """POST /api/generate returns 11 files and a download token."""
        _generate_and_assert_response(SEQUENTIAL_PAYLOAD)

    def test_download_zip_valid(self) -> None:
        """Download token returns a valid ZIP with all 11 files."""
        data = _generate_and_assert_response(SEQUENTIAL_PAYLOAD)
        _download_and_assert_zip(data["download_token"])

    def test_agent_py_imports_and_instances(self) -> None:
        """agent.py imports both SequentialAgent and LlmAgent, builds full tree."""
        data = _generate_and_assert_response(SEQUENTIAL_PAYLOAD)
        files = _download_and_assert_zip(data["download_token"])
        agent_py = files["agent.py"]

        _assert_python_syntax(agent_py, "agent.py")

        # Correct imports
        assert "from google.adk.agents import SequentialAgent" in agent_py
        assert "from google.adk.agents import LlmAgent" in agent_py
        assert "ParallelAgent" not in agent_py
        assert "LoopAgent" not in agent_py

        # Sub-agent instances
        assert "data_ingestion_agent = LlmAgent(" in agent_py
        assert "data_transform_agent = LlmAgent(" in agent_py
        assert "data_output_agent = LlmAgent(" in agent_py

        # Orchestrator instance
        assert "data_pipeline_orchestrator = SequentialAgent(" in agent_py
        assert "root_agent = data_pipeline_orchestrator" in agent_py

    def test_deterministic_tools_direct_call(self) -> None:
        """Deterministic tools called directly, not passed to LLM."""
        data = _generate_and_assert_response(SEQUENTIAL_PAYLOAD)
        files = _download_and_assert_zip(data["download_token"])
        agent_py = files["agent.py"]

        # normalize_records and validate_schema are deterministic → direct calls
        assert "normalize_records()" in agent_py
        assert "validate_schema()" in agent_py

        # Non-deterministic tools imported from tools module
        assert "fetch_raw_data" in agent_py
        assert "write_to_store" in agent_py

    def test_tools_py_has_all_tools(self) -> None:
        """tools.py contains all 5 tools with deterministic markers."""
        data = _generate_and_assert_response(SEQUENTIAL_PAYLOAD)
        files = _download_and_assert_zip(data["download_token"])
        tools_py = files["tools.py"]

        _assert_python_syntax(tools_py, "tools.py")
        assert "fetch_raw_data" in tools_py
        assert "normalize_records" in tools_py
        assert "validate_schema" in tools_py
        assert "write_to_store" in tools_py
        assert "# DETERMINISTIC" in tools_py

    def test_api_server_postgres_session(self) -> None:
        """api_server.py uses DatabaseSessionService for postgres backend."""
        data = _generate_and_assert_response(SEQUENTIAL_PAYLOAD)
        files = _download_and_assert_zip(data["download_token"])
        api_server = files["api_server.py"]

        _assert_python_syntax(api_server, "api_server.py")
        assert "DatabaseSessionService" in api_server
        assert "InMemorySessionService" not in api_server
        assert "postgresql+asyncpg://user:pass@localhost:5432/pipeline_db" in api_server

    def test_mcp_server_config_in_output(self) -> None:
        """Generated project references the SSE MCP server."""
        data = _generate_and_assert_response(SEQUENTIAL_PAYLOAD)
        files = _download_and_assert_zip(data["download_token"])

        # .env.example or CLAUDE.md should reference the MCP server
        combined = files["CLAUDE.md"] + files["LOAD_CONTEXT.md"]
        assert "data-api" in combined

    def test_topology_in_load_context(self) -> None:
        """LOAD_CONTEXT.md shows full agent tree."""
        data = _generate_and_assert_response(SEQUENTIAL_PAYLOAD)
        files = _download_and_assert_zip(data["download_token"])
        load_context = files["LOAD_CONTEXT.md"]

        assert "DataPipelineOrchestrator" in load_context
        assert "DataIngestionAgent" in load_context
        assert "DataTransformAgent" in load_context
        assert "DataOutputAgent" in load_context

    def test_todo_postgres_tasks_present(self) -> None:
        """TODO.md includes DATABASE_URL task for postgres backend."""
        data = _generate_and_assert_response(SEQUENTIAL_PAYLOAD)
        files = _download_and_assert_zip(data["download_token"])
        todo = files["TODO.md"]

        assert "DATABASE_URL" in todo

    def test_all_python_files_valid_syntax(self) -> None:
        """Every .py file in the ZIP parses without SyntaxError."""
        data = _generate_and_assert_response(SEQUENTIAL_PAYLOAD)
        files = _download_and_assert_zip(data["download_token"])
        for filename, content in files.items():
            if filename.endswith(".py"):
                _assert_python_syntax(content, filename)


# ---------------------------------------------------------------------------
# E2E: LLM Agent with MCP stdio server
# ---------------------------------------------------------------------------

class TestE2ELlmWithMCP:
    """Round-trip for an LLM agent with an MCP stdio server."""

    def test_generate_and_download(self) -> None:
        """Full generate → download cycle succeeds."""
        data = _generate_and_assert_response(LLM_WITH_MCP_PAYLOAD)
        _download_and_assert_zip(data["download_token"])

    def test_agent_py_single_llm(self) -> None:
        """agent.py wires a single LlmAgent with no orchestrator."""
        data = _generate_and_assert_response(LLM_WITH_MCP_PAYLOAD)
        files = _download_and_assert_zip(data["download_token"])
        agent_py = files["agent.py"]

        _assert_python_syntax(agent_py, "agent.py")
        assert "mcp_bot_agent = LlmAgent(" in agent_py
        assert "root_agent = mcp_bot_agent" in agent_py
        assert "SequentialAgent" not in agent_py

    def test_mcp_stdio_config_referenced(self) -> None:
        """MCP stdio server config appears in project context files."""
        data = _generate_and_assert_response(LLM_WITH_MCP_PAYLOAD)
        files = _download_and_assert_zip(data["download_token"])

        combined = files["CLAUDE.md"] + files["LOAD_CONTEXT.md"]
        assert "account-svc" in combined
        assert "stdio" in combined


# ---------------------------------------------------------------------------
# E2E: Error cases
# ---------------------------------------------------------------------------

class TestE2EValidationErrors:
    """API rejects invalid payloads with 422."""

    def test_llm_agent_with_sub_agents_rejected(self) -> None:
        """LLM agent cannot have sub_agents."""
        payload = {
            "project_name": "bad-agent",
            "description": "Should fail.",
            "root_agent": {
                "name": "BadAgent",
                "agent_type": "llm",
                "instructions": "Hello.",
                "sub_agents": [
                    {
                        "name": "Child",
                        "agent_type": "llm",
                        "instructions": "Oops.",
                    },
                ],
            },
        }
        resp = client.post("/api/generate", json=payload)
        assert resp.status_code == 422

    def test_sequential_agent_without_sub_agents_rejected(self) -> None:
        """Sequential agent must have at least one sub-agent."""
        payload = {
            "project_name": "empty-seq",
            "description": "Should fail.",
            "root_agent": {
                "name": "EmptySeq",
                "agent_type": "sequential",
                "instructions": "No children.",
                "sub_agents": [],
            },
        }
        resp = client.post("/api/generate", json=payload)
        assert resp.status_code == 422

    def test_postgres_without_db_url_rejected(self) -> None:
        """Postgres session backend requires db_url."""
        payload = {
            "project_name": "no-db-url",
            "description": "Should fail.",
            "root_agent": {
                "name": "Agent",
                "agent_type": "llm",
                "instructions": "Hello.",
            },
            "session": {"backend": "postgres"},
        }
        resp = client.post("/api/generate", json=payload)
        assert resp.status_code == 422

    def test_mcp_stdio_without_command_rejected(self) -> None:
        """MCP stdio mode requires a command."""
        payload = {
            "project_name": "bad-mcp",
            "description": "Should fail.",
            "root_agent": {
                "name": "Agent",
                "agent_type": "llm",
                "instructions": "Hello.",
            },
            "mcp_servers": [{"name": "bad", "mode": "stdio"}],
        }
        resp = client.post("/api/generate", json=payload)
        assert resp.status_code == 422

    def test_mcp_sse_without_url_rejected(self) -> None:
        """MCP SSE mode requires a url."""
        payload = {
            "project_name": "bad-mcp-sse",
            "description": "Should fail.",
            "root_agent": {
                "name": "Agent",
                "agent_type": "llm",
                "instructions": "Hello.",
            },
            "mcp_servers": [{"name": "bad", "mode": "sse"}],
        }
        resp = client.post("/api/generate", json=payload)
        assert resp.status_code == 422

    def test_invalid_download_token_returns_404(self) -> None:
        """Nonexistent download token returns 404."""
        resp = client.get("/api/download/nonexistent-token")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# E2E: Health endpoint
# ---------------------------------------------------------------------------

class TestE2EHealth:
    """Health endpoint always returns 200."""

    def test_health_returns_ok(self) -> None:
        """/health returns status ok."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "agentforge"


# ---------------------------------------------------------------------------
# E2E: Live runner endpoint
# ---------------------------------------------------------------------------

class TestE2ELiveRunner:
    """Live test runner returns a simulated execution trace."""

    def test_sequential_live_test_returns_trace(self) -> None:
        """Sequential topology returns child steps plus orchestrator summary."""
        resp = client.post(
            "/api/test-run",
            json={
                "config": SEQUENTIAL_PAYLOAD,
                "message": "Summarize the pipeline steps for this customer batch.",
            },
        )

        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["status"] == "ok"
        assert data["project_name"] == "data-pipeline"
        assert data["root_agent"] == "DataPipelineOrchestrator"
        assert data["input_message"] == "Summarize the pipeline steps for this customer batch."
        assert len(data["steps"]) == 4
        assert data["steps"][0]["agent_name"] == "DataIngestionAgent"
        assert data["steps"][0]["depth"] == 1
        assert data["steps"][-1]["agent_name"] == "DataPipelineOrchestrator"
        assert data["steps"][-1]["mode"] == "orchestrator"
        assert "DataTransformAgent" in data["final_output"]
        assert data["warnings"] == []

    def test_live_test_surfaces_missing_mcp_warning(self) -> None:
        """Configurations without MCP servers return a warning in the result."""
        resp = client.post(
            "/api/test-run",
            json={
                "config": SIMPLE_LLM_PAYLOAD,
                "message": "Run a quick smoke test.",
            },
        )

        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["steps"][0]["agent_name"] == "ChatbotAgent"
        assert "No MCP servers are configured for this run." in data["warnings"]
