import os
import readline
import atexit
from ollama import chat, Options

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
from sven.tools.task import add_task, current_task, cancel_task, complete_task, list_tasks
from sven.tools.grep import grep
from sven.tools.find import find
from sven.tools.memory_tools import (
    add_skill,
    list_skills,
    get_skill,
    update_skill,
    delete_skill,
    search_skills,
)

from sven.core import process_tool_calls
from sven.core import send
from sven.config import Config

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
    "add_task": add_task,
    "current_task": current_task,
    "list_tasks": list_tasks,
    "cancel_task": cancel_task,
    "complete_task": complete_task,
    "grep": grep,
    "find": find,

    # Skill / knowledge base
    'add_skill': add_skill,
    'list_skills': list_skills,
    'get_skill': get_skill,
    'update_skill': update_skill,
    'delete_skill': delete_skill,
    'search_skills': search_skills,
}

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
        send(user_prompt, messages, available_functions, config)

if __name__ == "__main__":
    interactive_chat()
