# src/mychat/chat.py
import json
from typing import Optional
import readline
from ollama import chat, Options

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
from sven.tools.task import add_task, current_task, cancel_task, complete_task

from sven.core import process_tool_calls
from sven.core import send


def load_config() -> dict:
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

available_functions = {
  'getdatetime': getdatetime,
  'websearch': websearch,
  'webfetch': webfetch,
  'manpage': manpage,
  'touch': touch,
  'listfiles': listfiles,
  'read': read,
  'searchandreplace': searchandreplace,
  'replacefile': replacefile,
  'replaceline': replaceline,
  'compilefile': compilefile,
  'compilefiles': compilefiles,
  'add_task': add_task,
  'current_task': current_task,
  'cancel_task': cancel_task,
  'complete_task': complete_task,
}

# Enable input history with arrow keys using readline (Unix). On Windows, the module may not be available.
def interactive_chat(
    model: str = None,
    options: Options | None = None,
    system_prompt: str = None,
) -> None:
    """
    Run an interactive LLM conversation in the termnal with config from JSON.

    Parameters
    ----------
    model : str, optional
        Ollama model name (e.g. 'gpt-oss:20b').
    options : Options, optional
        Generation parameters; if omitted a default of
        `temperature=0.0` is used.
    system_prompt : str, optional
        Initial system message that sets the assistant's role.
    """
    config = load_config()
    
    # Fallback to defaults if not in config or provided as arguments
    model = model or config.get("model", "gemma4:12b")
    system_prompt = system_prompt or config.get("system_prompt", "You are Sven. A senior Softwaredeveloper. Trust your toolcalls. Do not doublecheck if everything worked. A compile step will find problems for you.")
    
    if options is None:
        # Parse options from config
        opt_dict = config.get("options", {"temperature": 0.0})
        options = Options(**opt_dict)

    # Conversation history
    messages = [{"role": "system", "content": system_prompt}]

    while True:
        try:
            user_text = input("\n\x1b[34mUser\x1b[0m: ")
        except EOFError:  # Ctrl‑D (Unix) / Ctrl‑Z (Windows)
            print("\n[Conversation ended]")
            break

        if not user_text.strip():
            continue  # ignore empty lines

        send(user_text, messages, system_prompt, model, available_functions, options)
