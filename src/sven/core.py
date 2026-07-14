from pathlib import Path
from typing import Dict, List, Optional
from ollama import chat, Options, Client
import logging
import json
import pprint

from sven.history import store_history

# Setup a standard logger
logger = logging.getLogger(__name__)

writing_tools = ['replacefile', 'replaceline', 'touch']

input_tokens: int = 0
output_tokens: int = 0
_ollama_client: Optional[Client] = None

def get_ollama_client(config):
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = Client(host=config.host)
    return _ollama_client

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
    latest_thought = ""
    messages.append({"role": "user", "content": user_prompt})
    
    client = get_ollama_client(config)

    while True:
        if(len(messages) > config.max_messages):
            messages = summarize_conversation(user_prompt, latest_thought, messages, config)
        
        stream = client.chat(
            model=config.model,
            keep_alive=config.keep_alive,
            messages=messages,
            tools=tools,
            options=config.options.to_dict(),
            stream=True,
        )
        content = ""
        thought = ""
        print("\x1b[38;2;10;140;75m")
        thinking = True
        tool_calls=None
        try:
            for chunk in stream:
                if chunk.message.thinking is None and thinking:
                    if thought:
                        print("\x1b[0m\n")
                        latest_thought = thought
                    else:
                        print("\x1b[0m")
                    thinking = False
                if chunk.message.thinking is not None:
                    thought += chunk.message.thinking
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

SUMMARISER_SYSTEM_MSG = """
You are an assistant whose sole task is to produce a single paragraph that captures the essential facts of the conversation so far.
The paragraph must contain only the following elements (in any order):

1. The user’s stated preferences or constraints.
2. Concrete facts that have been verified during the chat.
3. Current goals or tasks that the user wants to accomplish.
4. Key decisions that have already been made.

Do not include pleasantries, greetings, filler text, self‑referential remarks, or internal system instructions.
If there is nothing to summarise, reply with an empty string.
Keep the output under 120 words so it can be safely embedded in subsequent messages.
"""

def summarize_conversation(
        user_prompt: str,
        latest_thought: str,
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

    client = get_ollama_client(config)
    stream = client.chat(
            model=config.model,
            keep_alive=config.keep_alive,
            options=config.options.to_dict(),
            messages=[
                {"role": "system", "content": SUMMARISER_SYSTEM_MSG },
                *old_context
                ],
            stream=True)
    print("\x1b[38;2;10;140;10m")
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
        print(f"\n\x1b[0m\x1b[1m\x1b[31min Error: \x1b[0m{e}\x1b[0m")
        return [];

    final_history = [
            {"role": "system", "content": config.system_prompt},
            {"role": "assistant", "content": f"history summary: {final_summary.strip()}"},
            #{"role": "user", "content": user_prompt},
            ]

    for m in new_context:
        if m["role"] != "system":
            final_history.append(m)

    if latest_thought:
        final_history.append({"role": "assistant", "content": f"latest thought: {latest_thought}"})
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

        #print(f"\n🛠\t\x1b[32m{func_name}\x1b[0m")
        print(f"\n\t🔧  \x1b[32m{func_name}\x1b[0m")
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
