import json
import pprint
from pathlib import Path
from typing import Dict, List, Optional
from ollama import chat, Options
import logging
import json

from sven.tools.task import add_task, current_task, cancel_task, complete_task, list_tasks
from sven.history import store_history

task_functions = {
  'add_task': add_task,
  'list_tasks': list_tasks,
  'cancel_task': cancel_task,
  'complete_task': complete_task,
}
from sven.skills import SkillRegistry

# Initialize the skill registry
skill_registry = SkillRegistry()

# Register all available skills
# Note: In a production environment, you might use a plugin system or 
# dynamic discovery to register these.
def register_tools():
    # This is currently a placeholder for manual registration if needed.
    pass

# The core logic now uses the skill registry instead of raw functions
# where applicable in the tool calling loop.


# Setup a standard logger
logger = logging.getLogger(__name__)

writing_tools = ['replacefile', 'replaceline', 'touch']

input_tokens: int = 0
output_tokens: int = 0

def _load_token_counts(config):
    global input_tokens, output_tokens
    token_file = Path(config.data_dir) / config.token_stats_file
    try:
        with open(token_file, "r") as f:
            data = json.load(f)
            input_tokens = data.get("input_tokens", 0)
            output_tokens = data.get("output_tokens", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        input_tokens = 0
        output_tokens = 0

def _save_token_counts(config):
    token_file = Path(config.data_dir) / config.token_stats_file
    token_file.parent.mkdir(parents=True, exist_ok=True)
    with open(token_file, "w") as f:
        json.dump({"input_tokens": input_tokens, "output_tokens": output_tokens}, f)

def send(user_prompt: str, messages: list, available_functions: Dict[str, any], config) ->  list:
    global input_tokens, output_tokens          # <‑‑ add this line
    _load_token_counts(config)
    tools = list(available_functions.values())
    messages.append({"role": "user", "content": user_prompt})
    while True:
        if(len(messages) > config.max_messages):
            messages = summarize_conversation(user_prompt, messages, config)
        stream = chat(
            model=config.model,
            messages=messages,
            tools=tools,
            options=config.options.to_dict(),
            stream=True,
        )
        content = ""
        print("\x1b[33m")
        thinking = True
        tool_calls=None
        try:
            for chunk in stream:
                if chunk.message.thinking is None and thinking:
                    print("\x1b[21m\n      \x1b[0m\n")
                    thinking = False
                if chunk.message.thinking is not None:
                    print(chunk.message.thinking, end="", flush=True)
                if chunk.message.content is not None:
                    content += chunk.message.content
                    print(chunk.message.content, end="", flush=True)
                if chunk.message.tool_calls is not None:
                    tool_calls = chunk.message.tool_calls
                if chunk.done:
                    input_tokens += chunk.prompt_eval_count
                    output_tokens += chunk.eval_count
                    _save_token_counts(config)
                    print(f"\n\x1b[1min {chunk.prompt_eval_count} out {chunk.eval_count} | used ({input_tokens}|{output_tokens})\x1b[0m")
                    response = chunk
                    break;
        except Exception as e:
            print(f"\n\x1b[1min Error: {e}\x1b[0m")
            break;

        response.message.content = content
        response.message.tool_calls = tool_calls
        messages = process_tool_calls(response.message, available_functions, messages)

        if not response.message.tool_calls:
            store_history(config, messages)
            break

def summarize_conversation(
        user_prompt: str,
        messages: list, 
        config,
        ) -> list:
    """
    "Summarize the following conversation into a concise, fact-heavy paragraph. "
    "Focus exclusively on user preferences, established facts, current goals, and key decisions. "
    "Omit all conversational filler, pleasantries, and internal system instructions."
    """
    global input_tokens, output_tokens          # <‑‑ add this line
    without_system = [m for m in messages if m["role"] != "system"]
    if len(without_system) <= config.keep_recent_count:
        return messages;

    old_context = without_system[:-config.keep_recent_count]
    new_context = without_system[-config.keep_recent_count:]

    stream = chat(
            model=config.model,
            options=config.options.to_dict(),
            messages=[
                {"role": "system", "content":
                 """
                 Provide a concise summary focusing on: [preferences, facts, goals, decisions]. Omit pleasantries and system notes.
                 """
                 },
                *old_context
                ],
            stream=True)
    print("\x1b[31m")
    final_summary = ""
    try:
        for chunk in stream:
            if chunk.message.thinking is not None:
                print(chunk.message.thinking, end="", flush=True)
            if chunk.message.content is not None:
                final_summary += chunk.message.content
                print(chunk.message.content, end="", flush=True)
            if chunk.done:
                input_tokens += chunk.prompt_eval_count
                output_tokens += chunk.eval_count
                _save_token_counts(config)
                print(f"\n\x1b[1min {chunk.prompt_eval_count} out {chunk.eval_count} | used ({input_tokens}|{output_tokens})\x1b[0m")
                break;
        print("\x1b[0m")
    except Exception as e:
        print(f"\n\x1b[0m\x1b[1min Error: {e}\x1b[0m")
        return [];
    final_history = [
            {"role": "system", "content": config.system_prompt},
            {"role": "assistant", "content": f"history summary: {final_summary}"},
            {"role": "user", "content": user_prompt}
            ]

    # Add the messages that were supposed to stay untouched (skipping any systemic ones)
    for m in new_context:
        if m["role"] != "system":
            final_history.append(m)
    return final_history

def process_tool_calls(
        message, 
        available_functions: Dict[str, any], 
        history: list
        ) -> list:
    """
    Process tool calls from a model response.

    Args:
        message: The message object returned by the Ollama client.
        available_functions: A map of function names to actual python callables.
        history: The current conversation history (list of dicts).

    Returns:
        The updated message list after processing tool calls.
    """
    if not message.tool_calls:
        history.append({
                'role': 'assistant',
                'content': message.content,
            })
        return history

    history.append({
            'role': 'assistant',
            'tool_calls': message.tool_calls,
        })

    for tc in message.tool_calls:
        func_name = tc.function.name
        print(f"Calling tool: {func_name}")
        if func_name not in available_functions:
            logger.error(f"Tool '{func_name}' is not available.")
            continue

        arguments = tc.function.arguments
        if func_name in writing_tools:
            logger.info(f"Executing file modification tool '{func_name}' with args: {arguments}")
        else:
            logger.info(f"Executing system tool '{func_name}' with args: {arguments}")

        try:
            result = available_functions[func_name](**arguments)
            
            # Consistent formatting for tool output content
            if isinstance(result, dict) and result.get("success"):
                content = result.get("data") if result.get("data") is not None else ""
                logger.debug(f"Tool '{func_name}' executed successfully.")
            else:
                # Handle cases where tool returns success=False or isn't a dict
                error_msg = "Unknown error"
                if isinstance(result, dict):
                    error_msg = result.get('message', 'Unknown error')
                
                logger.warning(f"Tool '{func_name}' failed: {error_msg}")
                content = f"Error: {error_msg}"

            history.append({
                "role": "tool", 
                "tool_name": func_name, 
                "content": str(content)
                })

        except Exception as e:
            logger.exception(f"Exception occurred while handling tool '{func_name}': {str(e)}")
            content = f"Error: {str(e)}"
            history.append({
                "role": "tool", 
                "tool_name": func_name, 
                "content": str(content)
                })
    return history
