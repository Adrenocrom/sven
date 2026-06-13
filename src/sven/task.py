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
from sven.tools.read import read
from sven.tools.edit import searchandreplace
from sven.tools.edit import replacefile
from sven.tools.edit import replaceline
from sven.tools.python import compilefiles

from sven.core import process_tool_calls
from sven.core import send

all_available_functions: Dict[str, Any] = {
  'getdatetime': getdatetime,
  'websearch': websearch,
  'webfetch': webfetch,
  'manpage': manpage,
  'read': read,
  'touch': touch,
  'listfiles': listfiles,
  'searchandreplace': searchandreplace,
  'replacefile': replacefile,
  'replaceline': replaceline,
  'compilefiles': compilefiles,
}

# Enable input history with arrow keys using readline (Unix). On Windows, the module may not be available.
def run_prompt_sequence(
    prompts: List[str],
    model: str,
    options: Options | None = None,
    available_functions: Dict[str, Any] = all_available_functions,
    system_prompt: str = "You are Sven! You search for files if you are not shure. And you persist the changes by yourself. Dont ask the user to do it for you.",
) -> None:
    if options is None:
        options = Options(temperature=0.1)

    messages = [{"role": "system", "content": system_prompt}]
    size = len(prompts)
    count = 1
    for prompt in prompts:
        print(f"Running {count} of up to {size} prompts...")
        count+=1

        send(prompt, messages, system_prompt, model, available_functions)
