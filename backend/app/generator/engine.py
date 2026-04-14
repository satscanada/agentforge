"""Rendering engine for scaffold templates."""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from app.models.agent_config import AgentDefinition, GeneratedFile, ScaffoldRequest


def _to_var_name(name: str) -> str:
    """Convert PascalCase agent name to a snake_case variable name."""
    s1 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s2 = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s1)
    return s2.lower()


class GeneratorEngine:
    """Render scaffold files from a scaffold request."""

    def __init__(self, config: ScaffoldRequest) -> None:
        """Initialise the engine with the scaffold configuration."""
        self.config = config
        template_dir = Path(__file__).parent / "templates"
        self.environment = Environment(
            loader=FileSystemLoader(template_dir),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.environment.globals["flatten_agents"] = self.flatten_agents
        self.environment.globals["reverse_flatten_agents"] = self.reverse_flatten_agents
        self.environment.globals["deterministic_tools"] = self.deterministic_tools
        self.environment.globals["nondeterministic_tools"] = self.nondeterministic_tools
        self.environment.globals["collect_agent_types"] = self.collect_agent_types
        self.environment.globals["collect_all_nondeterministic_tools"] = self.collect_all_nondeterministic_tools
        self.environment.filters["to_var_name"] = _to_var_name

    def render(self, template_name: str, filename: str) -> GeneratedFile:
        """Render a single template into a GeneratedFile."""
        template = self.environment.get_template(template_name)
        content = template.render(config=self.config, root_agent=self.config.root_agent).strip() + "\n"
        return GeneratedFile(filename=filename, content=content)

    def render_all(self) -> list[GeneratedFile]:
        """Render all scaffold files required for checkpoint 5."""
        return [
            self.render("agent.py.j2", "agent.py"),
            self.render("tools.py.j2", "tools.py"),
            self.render("callbacks.py.j2", "callbacks.py"),
            self.render("main.py.j2", "main.py"),
            self.render("api_server.py.j2", "api_server.py"),
            self.render("requirements.txt.j2", "requirements.txt"),
            self.render("env.example.j2", ".env.example"),
            self.render("CLAUDE.md.j2", "CLAUDE.md"),
            self.render("README.md.j2", "README.md"),
            self.render("LOAD_CONTEXT.md.j2", "LOAD_CONTEXT.md"),
            self.render("TODO.md.j2", "TODO.md"),
        ]

    @staticmethod
    def flatten_agents(agent: AgentDefinition) -> list[AgentDefinition]:
        """Return a depth-first flattened list of an agent tree."""
        agents = [agent]
        for sub_agent in agent.sub_agents:
            agents.extend(GeneratorEngine.flatten_agents(sub_agent))
        return agents

    @staticmethod
    def reverse_flatten_agents(agent: AgentDefinition) -> list[AgentDefinition]:
        """Return agents in bottom-up order (leaves first, root last)."""
        return list(reversed(GeneratorEngine.flatten_agents(agent)))

    @staticmethod
    def collect_agent_types(agent: AgentDefinition) -> set[str]:
        """Return the set of all agent_type values present in the tree."""
        return {a.agent_type.value for a in GeneratorEngine.flatten_agents(agent)}

    @staticmethod
    def collect_all_nondeterministic_tools(agent: AgentDefinition) -> list[str]:
        """Return deduplicated non-deterministic tool names across all agents."""
        seen: set[str] = set()
        tools: list[str] = []
        for a in GeneratorEngine.flatten_agents(agent):
            for tool in a.tools:
                if not tool.is_deterministic and tool.name not in seen:
                    seen.add(tool.name)
                    tools.append(tool.name)
        return tools

    @staticmethod
    def deterministic_tools(agent: AgentDefinition) -> list[str]:
        """Return deterministic tool names for an agent."""
        return [tool.name for tool in agent.tools if tool.is_deterministic]

    @staticmethod
    def nondeterministic_tools(agent: AgentDefinition) -> list[str]:
        """Return non-deterministic tool names for an agent."""
        return [tool.name for tool in agent.tools if not tool.is_deterministic]
