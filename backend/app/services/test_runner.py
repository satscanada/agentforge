"""Simulated live runner for previewing agent topology behavior."""

from __future__ import annotations

from app.models.agent_config import (
    AgentDefinition,
    AgentType,
    ScaffoldRequest,
    TestRunResponse,
    TestRunStep,
)


class LiveTestRunner:
    """Execute a lightweight simulated run across the configured topology."""

    def __init__(self, config: ScaffoldRequest) -> None:
        self.config = config
        self.steps: list[TestRunStep] = []

    def run(self, message: str) -> TestRunResponse:
        """Run the root agent and return a structured trace."""
        prompt = message.strip()
        final_output = self._run_agent(self.config.root_agent, prompt, depth=0)
        warnings = self._collect_warnings()
        return TestRunResponse(
            project_name=self.config.project_name,
            root_agent=self.config.root_agent.name,
            input_message=prompt,
            final_output=final_output,
            steps=self.steps,
            warnings=warnings,
        )

    def _run_agent(self, agent: AgentDefinition, message: str, depth: int) -> str:
        if agent.agent_type == AgentType.LLM:
            return self._run_llm_agent(agent, message, depth)
        if agent.agent_type == AgentType.SEQUENTIAL:
            return self._run_sequential_agent(agent, message, depth)
        if agent.agent_type == AgentType.PARALLEL:
            return self._run_parallel_agent(agent, message, depth)
        return self._run_loop_agent(agent, message, depth)

    def _run_llm_agent(self, agent: AgentDefinition, message: str, depth: int) -> str:
        tools = [tool.name for tool in agent.tools]
        output = self._compose_llm_output(agent, message)
        summary = f"Interpreted the prompt using {len(tools)} configured tool(s)."
        self.steps.append(
            TestRunStep(
                agent_name=agent.name,
                agent_type=agent.agent_type,
                depth=depth,
                mode="agent",
                summary=summary,
                tools_used=tools,
                output=output,
            )
        )
        return output

    def _run_sequential_agent(self, agent: AgentDefinition, message: str, depth: int) -> str:
        current_message = message
        child_outputs: list[str] = []
        for child in agent.sub_agents:
            child_output = self._run_agent(child, current_message, depth + 1)
            child_outputs.append(f"{child.name}: {child_output}")
            current_message = child_output

        output = "\n".join(child_outputs) if child_outputs else "No sub-agents were available to run."
        self.steps.append(
            TestRunStep(
                agent_name=agent.name,
                agent_type=agent.agent_type,
                depth=depth,
                mode="orchestrator",
                summary=f"Ran {len(agent.sub_agents)} sub-agent(s) in sequence.",
                output=output,
            )
        )
        return output

    def _run_parallel_agent(self, agent: AgentDefinition, message: str, depth: int) -> str:
        child_outputs = [
            f"{child.name}: {self._run_agent(child, message, depth + 1)}"
            for child in agent.sub_agents
        ]
        output = "\n".join(child_outputs) if child_outputs else "No parallel branches were available to run."
        self.steps.append(
            TestRunStep(
                agent_name=agent.name,
                agent_type=agent.agent_type,
                depth=depth,
                mode="orchestrator",
                summary=f"Ran {len(agent.sub_agents)} sub-agent branch(es) in parallel simulation.",
                output=output,
            )
        )
        return output

    def _run_loop_agent(self, agent: AgentDefinition, message: str, depth: int) -> str:
        current_message = message
        loop_outputs: list[str] = []
        for iteration in range(1, 3):
            for child in agent.sub_agents:
                current_message = self._run_agent(child, current_message, depth + 1)
                loop_outputs.append(f"Iteration {iteration} · {child.name}: {current_message}")

        output = "\n".join(loop_outputs) if loop_outputs else "No loop sub-agents were available to run."
        self.steps.append(
            TestRunStep(
                agent_name=agent.name,
                agent_type=agent.agent_type,
                depth=depth,
                mode="orchestrator",
                summary="Completed 2 simulated loop iteration(s) across child agents.",
                output=output,
            )
        )
        return output

    def _compose_llm_output(self, agent: AgentDefinition, message: str) -> str:
        tool_clause = self._build_tool_clause(agent)
        instruction_focus = agent.instructions.strip().rstrip(".")
        model_name = agent.model or self.config.litellm.model
        return (
            f"{agent.name} reviewed the prompt \"{message}\". "
            f"Instruction focus: {instruction_focus}. "
            f"Model path: {model_name}. "
            f"{tool_clause}"
        )

    @staticmethod
    def _build_tool_clause(agent: AgentDefinition) -> str:
        if not agent.tools:
            return "No tools were configured for this agent."

        deterministic_tools = [tool.name for tool in agent.tools if tool.is_deterministic]
        dynamic_tools = [tool.name for tool in agent.tools if not tool.is_deterministic]
        parts: list[str] = []
        if deterministic_tools:
            parts.append(f"Deterministic tools: {', '.join(deterministic_tools)}.")
        if dynamic_tools:
            parts.append(f"Context tools: {', '.join(dynamic_tools)}.")
        return " ".join(parts)

    def _collect_warnings(self) -> list[str]:
        warnings: list[str] = []
        if not self.config.mcp_servers:
            warnings.append("No MCP servers are configured for this run.")
        if self.config.session.backend == "postgres" and not self.config.session.db_url:
            warnings.append("Postgres session backend is selected without a database URL.")
        return warnings
