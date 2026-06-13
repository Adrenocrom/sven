# src/mychat/chat.py
import json
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
from sven.tools.python import compilefile

from sven.core_logic import process_tool_calls

available_functions = {
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
  'compilefile': compilefile,
}
tools = list(available_functions.values())

# Enable input history with arrow keys using readline (Unix). On Windows, the module may not be available.
def interactive_chat(
    model: str,
    options: Options | None = None,
    system_prompt: str = "You are Sven. A senior Softwaredeveloper. Trust your toolcalls. Do not doublecheck if everything worked. A compile step will find problems for you.",
) -> None:
    """
    Run an interactive LLM conversation in the terminal.

    Parameters
    ----------
    model : str
        Ollama model name (e.g. 'gpt-oss:20b').
    options : Options, optional
        Generation parameters; if omitted a default of
        `temperature=0.0` is used.
    system_prompt : str, optional
        Initial system message that sets the assistant's role.
    """
    if options is None:
        options = Options(temperature=0.0)

    # Conversation history
    messages = [{"role": "system", "content": system_prompt}]

    latest_prompt_eval_count = 0
    while True:
        try:
            user_text = input("\n\x1b[34mUser\x1b[0m: ")
        except EOFError:  # Ctrl‑D (Unix) / Ctrl‑Z (Windows)
            print("\n[Conversation ended]")
            break

        if not user_text.strip():
            continue  # ignore empty lines

        if latest_prompt_eval_count > 65536:
            summary_context = [m for m in messages if m["role"] != "system"]
            summary_response = chat(
                model=model,
                messages=[
                    {"role": "system", "content": "Summarize the following conversation briefly while retaining all key information and context. Do not include system instructions or persona details."},
                    *summary_context
                ],
            )
            # Replace history with summarized version (keeping the original system prompt at index 0)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "assistant", "content": f"Summary of previous conversation: {summary_response.message.content}"}
            ]

        messages.append({"role": "user", "content": user_text})
        while True:
            response: ChatResponse = chat(
                model=model,
                messages=messages,
                tools=tools
            )
            latest_prompt_eval_count = response.get('prompt_eval_count')
            print(f"Prompt tokens: {response.get('prompt_eval_count')}")
            print(f"Output tokens: {response.get('eval_count')}")
            if response.message.thinking is not None:
                print(f"Thinking: \x1b[33m{response.message.thinking}\x1b[0m")
            messages.extend(process_tool_calls(response.message, available_functions, messages))

            if not response.message.tool_calls:
                print(f"\x1b[31mSven\033[0m: {response.message.content}")
                break
