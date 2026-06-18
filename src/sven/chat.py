import json
from typing import Optional
import readline
from ollama import chat, Options

# from sven.history import load_history

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
}

# Enable input history with arrow keys using readline (Unix). On Windows, the module may not be available.
def interactive_chat() -> None:
    """Run an interactive LLM conversation in the terminal with config from JSON."""
    config = Config.load()
    # messages = load_history()
    messages = []
    messages.append({"role": "system", "content": config.system_prompt})
    while True:
        try:
            user_prompt = input("\n\x1b[34mUser\x1b[0m: ")
        except EOFError:
            print("\n[Conversation ended]")
            break
        if not user_prompt.strip():
            continue  # ignore empty lines
        send(user_prompt, messages, available_functions, config)

if __name__ == "__main__":
    interactive_chat()
