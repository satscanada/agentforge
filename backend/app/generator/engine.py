"""Rendering engine for scaffold templates."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from app.models.agent_config import AgentDefinition, GeneratedFile, ScaffoldRequest


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
        self.environment.globals["deterministic_tools"] = self.deterministic_tools
        self.environment.globals["nondeterministic_tools"] = self.nondeterministic_tools

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
    def deterministic_tools(agent: AgentDefinition) -> list[str]:
        """Return deterministic tool names for an agent."""
        return [tool.name for tool in agent.tools if tool.is_deterministic]

    @staticmethod
    def nondeterministic_tools(agent: AgentDefinition) -> list[str]:
        """Return non-deterministic tool names for an agent."""
        return [tool.name for tool in agent.tools if not tool.is_deterministic]
