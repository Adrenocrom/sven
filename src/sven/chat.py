# src/mychat/chat.py
import json
from ollama import chat, Options

from sven.tools.getdatetime import getdatetime
from sven.tools.websearch import websearch
from sven.tools.manpage import manpage
from sven.tools.touch import touch
from sven.tools.listfiles import listfiles
from sven.tools.vim.read import read
from sven.tools.vim.edit import replacefile
from sven.tools.vim.edit import replaceline
from sven.tools.vim.autoformat import autoformat

available_functions = {
  'getdatetime': getdatetime,
  'websearch': websearch,
  'manpage': manpage,
  'autoformat': autoformat,
  'read': read,
  'touch': touch,
  'listfiles': listfiles,
  'replacefile': replacefile,
  'replaceline': replaceline,
}
tools = list(available_functions.values())

def interactive_chat(
    model: str,
    options: Options | None = None,
    system_prompt: str = "You are a helpful assistant.",
) -> None:
    """
    Run an interactive LLM conversation in the terminal.

    Parameters
    ----------
    model : str
        Ollama model name (e.g. 'gpt-oss:20b').
    options : Options, optional
        Generation parameters; if omitted a default of
        `temperature=0.3` is used.
    system_prompt : str, optional
        Initial system message that sets the assistant's role.
    """
    if options is None:
        options = Options(temperature=0.3)

    # Conversation history
    messages = [{"role": "system", "content": system_prompt}]

    while True:
        try:
            user_text = input("\nUser: ")
        except EOFError:  # Ctrl‑D (Unix) / Ctrl‑Z (Windows)
            print("\n[Conversation ended]")
            break

        if not user_text.strip():
            continue  # ignore empty lines

        messages.append({"role": "user", "content": user_text})

        while True:
            response: ChatResponse = chat(
                model=model,
                messages=messages,
                tools=tools
            )
            messages.append(response.message)
            #print(f"Thinking: \x1b[30m{response.message.thinking}\x1b[0m")
            if response.message.tool_calls:
                for tc in response.message.tool_calls:
                    if tc.function.name in available_functions:
                        print(f"\x1b[33m\ttoolcall {tc.function.name} with arguments {tc.function.arguments}\x1b[0m")
                        result = available_functions[tc.function.name](**tc.function.arguments)
                        #print(f"Result: {result}")
                        # add the tool result to the messages
                        messages.append({'role': 'tool', 'tool_name': tc.function.name, 'content': str(result)})
            else:
                print(f"\x1b[31mSven\033[0m: {response.message.content}")
                # end the loop when there are no more tool calls
                break
