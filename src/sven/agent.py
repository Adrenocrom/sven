import copy

from sven.core import send
from sven.config import Config


class Agent:
    """A reusable LLM agent with its own system prompt and tool set."""

    def __init__(
        self,
        config: Config,
        system_prompt: str,
        available_functions: dict,
        name: str = "Agent",
    ):
        self.config = copy.deepcopy(config)
        self.config.system_prompt = system_prompt
        self.available_functions = available_functions
        self.name = name
        self.messages = [{"role": "system", "content": self.config.system_prompt}]

    def run(self, user_prompt: str) -> str:
        """Send a prompt to the agent and return its text response."""
        send(user_prompt, self.messages, self.available_functions, self.config)
        return self.messages[-1]["content"]
