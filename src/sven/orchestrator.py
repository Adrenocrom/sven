from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Callable

from sven.agent import Agent
from sven.config import Config


@dataclass
class AgentRole:
    """Description of an agent's role for routing decisions."""

    name: str
    description: str
    skills: list[str]


class AgentOrchestrator:
    """Route tasks to the most appropriate registered agent.

    The orchestrator maintains a collection of agents and decides which one
    should handle a user prompt. Routing can be keyword-based or delegated to
    a small LLM router agent.
    """

    def __init__(self, config: Config, router: Agent | None = None):
        self.config = config
        self.agents: dict[str, Agent] = {}
        self.roles: dict[str, AgentRole] = {}
        self.router = router

    def register(
        self,
        name: str,
        agent: Agent,
        description: str = "",
        skills: list[str] | None = None,
    ) -> None:
        """Register an agent and its role metadata."""
        self.agents[name] = agent
        self.roles[name] = AgentRole(
            name=name,
            description=description,
            skills=skills or [],
        )

    def list_agents(self) -> list[AgentRole]:
        """Return metadata for all registered agents."""
        return list(self.roles.values())

    def route(self, task: str) -> Agent:
        """Pick the best agent for the given task.

        If a router agent is configured, it is used to make an LLM-based
        decision. Otherwise a simple keyword match against role descriptions
        and skills is used.
        """
        if self.router is not None:
            return self._route_with_llm(task)
        return self._route_with_keywords(task)

    def _route_with_keywords(self, task: str) -> Agent:
        task_lower = task.lower()
        best_name: str | None = None
        best_score = -1

        for name, role in self.roles.items():
            score = 0
            if role.description and any(
                word in task_lower for word in role.description.lower().split()
            ):
                score += 1
            for skill in role.skills:
                if skill.lower() in task_lower:
                    score += 2
            if score > best_score:
                best_score = score
                best_name = name

        if best_name is None or best_name not in self.agents:
            return next(iter(self.agents.values()))
        return self.agents[best_name]

    def _route_with_llm(self, task: str) -> Agent:
        catalog = "\n".join(
            f"- {role.name}: {role.description} [skills: {', '.join(role.skills)}]"
            for role in self.roles.values()
        )
        prompt = (
            "You are a task router. Given the user task below, pick exactly one "
            "agent name from the catalog that is best suited to handle it. "
            "Respond with only the agent name and nothing else.\n\n"
            f"Available agents:\n{catalog}\n\n"
            f"Task: {task}\n\nAgent name:"
        )
        selected = self.router.run(prompt).strip()
        if selected in self.agents:
            return self.agents[selected]
        return self._route_with_keywords(task)

    def run(self, user_prompt: str, verbose: bool = True) -> str:
        """Route the prompt to an agent and return its response."""
        agent = self.route(user_prompt)
        if verbose:
            r, g, b = agent.rgb
            print(
                f"\n\x1b[38;2;{r};{g};{b}m{agent.name}\x1b[0m "
                f"(orchestrator routed): {user_prompt}"
            )
        return agent.run(user_prompt)


def build_default_orchestrator(
    config: Config,
    available_functions: dict[str, Callable],
    include_router: bool = False,
) -> AgentOrchestrator:
    """Create an orchestrator with a small set of default agents."""
    orchestrator = AgentOrchestrator(config)

    if include_router:
        router_agent = Agent(
            config=config,
            system_prompt=(
                "You are a task router. Pick the single best agent for a task. "
                "Reply with only the agent name."
            ),
            available_functions=available_functions,
            name="Router",
        )
        orchestrator.router = router_agent

    prompt_optimizer = Agent(
        config=config,
        system_prompt=(
            "You are Greg, a prompt optimization agent. "
            "1. Check spelling and grammar. "
            "2. Keep the original meaning. "
            "3. If it's a bigger task, define a goal and the first steps. "
            "Do not add explanations or wrappers."
        ),
        available_functions=available_functions,
        name="Greg (Prompt Optimizer)",
    )
    orchestrator.register(
        name="prompt_optimizer",
        agent=prompt_optimizer,
        description="Improves user prompts for clarity and completeness.",
        skills=["prompt optimization", "grammar", "task planning"],
    )

    coder = Agent(
        config=config,
        system_prompt=(
            "You are Sven, a senior software developer. "
            "Write clean, correct, and well-tested code. "
            "Explain trade-offs when asked."
        ),
        available_functions=available_functions,
        name="Sven (Coder)",
    )
    orchestrator.register(
        name="coder",
        agent=coder,
        description="Writes and edits code, runs tests, and fixes bugs.",
        skills=["python", "rust", "java", "testing", "refactoring"],
    )

    researcher = Agent(
        config=config,
        system_prompt=(
            "You are a research agent. Use web search and documentation tools "
            "to find accurate, up-to-date information. Summarize sources."
        ),
        available_functions=available_functions,
        name="Researcher",
    )
    orchestrator.register(
        name="researcher",
        agent=researcher,
        description="Finds documentation, examples, and current facts online.",
        skills=["web search", "documentation", "research"],
    )

    reviewer = Agent(
        config=config,
        system_prompt=(
            "You are a code reviewer. Check for bugs, style issues, security "
            "problems, and missing tests. Be concise and actionable."
        ),
        available_functions=available_functions,
        name="Reviewer",
    )
    orchestrator.register(
        name="reviewer",
        agent=reviewer,
        description="Reviews code and suggests improvements.",
        skills=["code review", "security", "testing"],
    )

    return orchestrator
