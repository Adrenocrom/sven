# src/sven/task.py
import json
import readline
from typing import List, Dict, Any
from ollama import chat, Options

from sven.tools.getdatetime import getdatetime
from sven.tools.websearch import websearch
from sven.tools.webfetch import webfetch
from sven.tools.manpage import manpage
from sven.tools.touch import touch
from sven.tools.listfiles import listfiles
from sven.tools.vim.read import read
from sven.tools.vim.edit import searchandreplace
from sven.tools.vim.edit import replacefile
from sven.tools.vim.edit import replaceline
from sven.tools.python.compilefile import compilefile

# Importing the shared logic to reduce redundancy
from sven.core_logic import process_tool_calls

available_functions: Dict[str, Any] = {
  'getdatetime': getdatetime,
  'websearch': websearch,
  'webfetch': webfetch,
  'manpage': manpage,
  'read': read,
  'touch': touch,
  'listfiles': listfiles,
  #'searchandreplace': searchandreplace,
  'replacefile': replacefile,
  'replaceline': replaceline,
  'compilefile': compilefile,
}
tools = list(available_functions.values())

# Enable input history with arrow keys using readline (Unix). On Windows, the module may not be available.
def run_prompt_sequence(
    prompts: List[str],
    model: str,
    options: Options | None = None,
    system_prompt: str = "You are Sven, you search for files if you are not shure. And you persist the changes by yourself. Dont ask the user to do it for you.",
) -> None:
    if options is None:
        options = Options(temperature=0.0)

    messages = [{"role": "system", "content": system_prompt}]
    size = len(prompts)
    count = 1
    for prompt in prompts:
        print(f"Running {count} of up to {size} prompts...")
        messages.append({"role": "user", "content": prompt})

        while True:
            response = chat(
                model=model,
                messages=messages,
                tools=tools
            )
            # The response message and any subsequent tool calls are handled by the core logic module
            messages.extend(process_tool_calls(response.message, available_functions, messages))

            if not response.message.tool_calls:
                print(f"{response.message.content}")
                break

