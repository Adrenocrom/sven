import os
import readline
import atexit
import pprint
import copy

from sven.history import load_history

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
    system_prompt = """
    You are Greg. You are a prompt building agent.

    1. Check for spelling and grammar.
    2. Keep the original meaning.
    3. check your skills with `list_skills`
    4. Check if some skills could be helpful and suggest them.
    5. Do not add explanations.
    6. If it's a bigger task, define a goal and maybe the first steps.
    """

    agent = Agent(
        config=config,
        system_prompt=system_prompt,
        available_functions=available_functions,
        name="Greg (Prompt Optimizer)",
    )

    instruction = f"""
        Please optimize the given user prompt:\n\n
        {user_prompt}\n\n
        Dont add explaination or wrapper!
        """

    new_user_prompt = agent.run(instruction)
    print(f"\n\x1b[35m{agent.name}\x1b[0m: {new_user_prompt}")
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
            user_prompt = input("\n\x1b[34mUser\x1b[0m: ")
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
