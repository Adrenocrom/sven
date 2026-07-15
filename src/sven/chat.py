import os
import readline
import atexit
import pprint
import copy

from sven.history import load_history

from sven.color import BLUE
from sven.color import RESET

from sven.tools.getdatetime import getdatetime
from sven.tools.websearch import websearch
from sven.tools.webfetch import webfetch
from sven.tools.manpage import manpage
from sven.tools.touch import touch
from sven.tools.listfiles import listfiles
from sven.tools.read import read
from sven.tools.edit import searchandreplace
from sven.tools.edit import replacefile
from sven.tools.edit import replaceline
from sven.tools.python import compilefile, compilefiles
from sven.tools.rust import cargo_build
from sven.tools.java import maven_clean_install
from sven.tools.dotnet import dotnet_build
from sven.tools.task import add_task, current_task, cancel_task, complete_task, list_tasks
from sven.tools.grep import grep
from sven.tools.find import find
from sven.tools.git import diff
from sven.tools.memory_tools import (
    add_skill,
    list_skills,
    get_skill,
    update_skill,
    delete_skill,
    search_skills,
)

from sven.core import process_tool_calls
from sven.config import Config
from sven.agent import Agent
from sven.core import send

available_functions = {
    "getdatetime": getdatetime,
    "websearch": websearch,
    "webfetch": webfetch,
    "manpage": manpage,
    "touch": touch,
    "listfiles": listfiles,
    "read": read,
    "searchandreplace": searchandreplace,
    "replacefile": replacefile,
    "replaceline": replaceline,
    "compilefile": compilefile,
    "compilefiles": compilefiles,
    "cargo_build": cargo_build,
    "maven_clean_install": maven_clean_install,
    "dotnet_build": dotnet_build,
    "add_task": add_task,
    "current_task": current_task,
    "list_tasks": list_tasks,
    "cancel_task": cancel_task,
    "complete_task": complete_task,
    "grep": grep,
    "find": find,
    "diff": diff,

    # Skill / knowledge base
    'add_skill': add_skill,
    'list_skills': list_skills,
    'get_skill': get_skill,
    'update_skill': update_skill,
    'delete_skill': delete_skill,
    'search_skills': search_skills,
}

def promptAgent(config, user_prompt) -> str:
    system_prompt = """You are Greg, a Prompt Optimization Agent. Your goal is to improve user prompts for clarity, grammar, and effectiveness while preserving their original intent.
    ## Rules
    1. Fix spelling and grammar errors.
    2. Enhance structure and clarity without changing the core meaning.
    3. Check available skills via `list_skills`. If a skill is relevant, mention it briefly at the very end (only if truly useful).
    4. For complex tasks, embed a clear goal and initial steps directly into the optimized prompt.

    ## Output Format
    - Return ONLY the raw text of the optimized prompt.
    - NO introductory phrases (e.g., "Here is your optimized prompt").
    - NO markdown code blocks (no ``` or quotes) unless the user explicitly used them in the original.
    - NO explanations or commentary after the output.
    """

    agent = Agent(
        config=config,
        system_prompt=system_prompt,
        available_functions=available_functions,
        name="Greg (Prompt Optimizer)",
    )

    instruction = f"""Optimize the following prompt for clarity, grammar, and effectiveness.
    Original Prompt:
    ---
    {user_prompt}
    ---
    Return only the optimized version with no additional text."""

    new_user_prompt = agent.run(instruction)
    r, g, b = agent.rgb
    print(f"\n\x1b[38;2;{r};{g};{b}m{agent.name}\x1b[0m: {new_user_prompt}")
    return new_user_prompt

def interactive_chat() -> None:
    """Run an interactive LLM conversation in the terminal.

    Prompts are stored in a readline history file located under the directory
    defined by ``Config.data_dir`` (default ``~/.local/share/sven``). This enables
    the up/down arrow keys to toggle through previous prompts, persisting across
    sessions.
    """
    config = Config.load()
    # Ensure the data directory exists
    os.makedirs(config.data_dir, exist_ok=True)
    _history_file = os.path.join(config.data_dir, "prompt_history")
    # Load existing history if present
    if os.path.exists(_history_file):
        try:
            readline.read_history_file(_history_file)
        except Exception:
            pass
    # Save history on program exit
    atexit.register(lambda: readline.write_history_file(_history_file))
    # Limit history length to avoid unbounded growth
    readline.set_history_length(1000)

    messages = load_history(config)
    messages.append({"role": "system", "content": config.system_prompt})

    while True:
        try:
            user_prompt = input(f"\n{BLUE}User{RESET}: ")
            #user_prompt = input("\n\x1b[34mUser\x1b[0m: ")
        except EOFError:
            print("\n[Conversation ended]")
            break
        except KeyboardInterrupt:
            print("\n[Conversation ended]")
            break
        if not user_prompt.strip():
            continue  # ignore empty lines
        # input() automatically adds the line to readline history
        new_user_prompt = promptAgent(config, user_prompt)
        send(new_user_prompt, messages, available_functions, config)

if __name__ == "__main__":
    interactive_chat()
