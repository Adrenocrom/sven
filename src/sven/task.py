# src/mychat/chat.py
import json
import readline
from ollama import chat, Options

from sven.tools.getdatetime import getdatetime
from sven.tools.websearch import websearch
from sven.tools.manpage import manpage
from sven.tools.touch import touch
from sven.tools.listfiles import listfiles
from sven.tools.vim.read import read
from sven.tools.vim.edit import searchandreplace
from sven.tools.vim.edit import replacefile
from sven.tools.vim.edit import replaceline
from sven.tools.vim.autoformat import autoformat
from sven.tools.python.compilefile import compilefile

available_functions = {
  'getdatetime': getdatetime,
  'websearch': websearch,
  'manpage': manpage,
  'autoformat': autoformat,
  'read': read,
  'touch': touch,
  'listfiles': listfiles,
  'searchandreplace': searchandreplace,
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
    for prompt in prompts:
        messages.append({"role": "user", "content": prompt})

        while True:
            response: ChatResponse = chat(
                model=model,
                messages=messages,
                tools=tools
            )
            messages.append(response.message)
            if response.message.tool_calls:
                for tc in response.message.tool_calls:
                    if tc.function.name in available_functions:
                        print(f"\x1b[33m\ttoolcall {tc.function.name} with arguments {tc.function.arguments}\x1b[0m")
                        result = available_functions[tc.function.name](**tc.function.arguments)
                        if result.get("success"):
                            content = result.get("data") if result.get("data") is not None else ""
                        else:
                            content = f"Error: {result.get('message')}"
                        messages.append({"role": "tool", "tool_name": tc.function.name, "content": str(content)})
            else:
                print(f"\x1b[31mSven\033[0m: {response.message.content}")
                break

