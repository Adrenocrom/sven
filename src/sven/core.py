from typing import Dict, List, Optional, Any
from pathlib import Path
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

def send(user_prompt: str, messages: list, available_functions: Dict[str, Any], config) -> list:
    global input_tokens, output_tokens
    _load_token_counts(config)
    tools = list(available_functions.values())
    latest_thought = ""
    messages.append({"role": "user", "content": user_prompt})

    client = get_ollama_client(config)

    while True:
        if len(messages) > config.max_messages:
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
        tool_calls = None
        response = None
        try:
            for chunk in stream:
                response = chunk
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
                    break
        except KeyboardInterrupt:
            print("\n\x1b[1mStopping...\x1b[0m")
            try:
                stream.close()
            except Exception:
                pass
            return messages
        except Exception as e:
            print(f"\n\x1b[1mError: {e}\x1b[0m")
            return messages

        if response is None:
            return messages

        response.message.content = content
        response.message.tool_calls = tool_calls
        messages = process_tool_calls(response.message, available_functions, messages)

        if not response.message.tool_calls:
            store_history(config, messages)
            break

    return messages

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
    global input_tokens, output_tokens
    without_system = [m for m in messages if m["role"] != "system"]
    if len(without_system) <= config.keep_recent_count:
        return messages

    old_context = without_system[:-config.keep_recent_count]
    new_context = without_system[-config.keep_recent_count:]

    client = get_ollama_client(config)
    stream = client.chat(
            model=config.model,
            keep_alive=config.keep_alive,
            options=config.options.to_dict(),
            messages=[
                {"role": "system", "content": SUMMARISER_SYSTEM_MSG},
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
                break
        print("\x1b[0m")
    except Exception as e:
        print(f"\n\x1b[0m\x1b[1m\x1b[31mError: \x1b[0m{e}\x1b[0m")
        return messages

    final_history = [
            {"role": "system", "content": config.system_prompt},
            {"role": "assistant", "content": f"history summary: {final_summary.strip()}"},
            ]

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

def get_model_info_summary(config, model_name: str) -> dict:
    """
    Return a concise summary of model information.
    """
    return {
        "name": model_name,
        "exists": model_exists(config, model_name),
        "running": is_model_running(config, model_name),
        "size": get_model_size(config, model_name),
        "parameter_size": get_model_parameter_size(config, model_name),
        "quantization_level": get_model_quantization_level(config, model_name),
        "families": get_model_families(config, model_name),
        "capabilities": get_model_capabilities(config, model_name),
    }

def get_server_info(config) -> dict:
    """
    Return basic information about the Ollama server.
    """
    return {
        "version": version(config),
        "base_url": getattr(config, "base_url", None),
        "default_model": get_default_model(config),
    }

def get_token_counts(config) -> dict:
    """
    Return the current input/output token counts.
    """
    _load_token_counts(config)
    return {"input_tokens": input_tokens, "output_tokens": output_tokens}

def set_token_counts(config, input_count: int, output_count: int):
    """
    Set the input/output token counts directly.
    """
    global input_tokens, output_tokens
    input_tokens = input_count
    output_tokens = output_count
    _save_token_counts(config)

def reset_token_counts(config):
    """
    Reset the input/output token counts to zero.
    """
    set_token_counts(config, 0, 0)

def increment_token_counts(config, input_count: int = 0, output_count: int = 0):
    """
    Increment the input/output token counts.
    """
    _load_token_counts(config)
    set_token_counts(config, input_tokens + input_count, output_tokens + output_count)

def model_exists(config, model_name: str) -> bool:
    """
    Check if a model exists on the Ollama server.
    """
    try:
        client = get_ollama_client(config)
        models = client.list().get("models", [])
        return any(m.get("model") == model_name or m.get("name") == model_name for m in models)
    except Exception as e:
        logger.error(f"Failed to check if model '{model_name}' exists: {e}")
        return False

def is_model_running(config, model_name: str) -> bool:
    """
    Check if a model is currently running on the Ollama server.
    """
    try:
        client = get_ollama_client(config)
        running = client.ps().get("models", [])
        return any(m.get("model") == model_name or m.get("name") == model_name for m in running)
    except Exception as e:
        logger.error(f"Failed to check if model '{model_name}' is running: {e}")
        return False

def get_model_size(config, model_name: str) -> Optional[int]:
    """
    Return the size of a model in bytes.
    """
    try:
        client = get_ollama_client(config)
        models = client.list().get("models", [])
        for m in models:
            if m.get("model") == model_name or m.get("name") == model_name:
                return m.get("size")
        return None
    except Exception as e:
        logger.error(f"Failed to get size for model '{model_name}': {e}")
        return None

def get_model_parameter_size(config, model_name: str) -> Optional[str]:
    """
    Return the parameter size of a model (e.g. '7B').
    """
    try:
        client = get_ollama_client(config)
        models = client.list().get("models", [])
        for m in models:
            if m.get("model") == model_name or m.get("name") == model_name:
                return m.get("parameter_size")
        return None
    except Exception as e:
        logger.error(f"Failed to get parameter size for model '{model_name}': {e}")
        return None

def get_model_quantization_level(config, model_name: str) -> Optional[str]:
    """
    Return the quantization level of a model.
    """
    try:
        client = get_ollama_client(config)
        models = client.list().get("models", [])
        for m in models:
            if m.get("model") == model_name or m.get("name") == model_name:
                return m.get("quantization_level")
        return None
    except Exception as e:
        logger.error(f"Failed to get quantization level for model '{model_name}': {e}")
        return None

def get_model_families(config, model_name: str) -> List[str]:
    """
    Return the families of a model.
    """
    try:
        client = get_ollama_client(config)
        models = client.list().get("models", [])
        for m in models:
            if m.get("model") == model_name or m.get("name") == model_name:
                families = m.get("details", {}).get("families", [])
                return families if isinstance(families, list) else []
        return []
    except Exception as e:
        logger.error(f"Failed to get families for model '{model_name}': {e}")
        return []

def get_model_capabilities(config, model_name: str) -> List[str]:
    """
    Return the capabilities of a model.
    """
    try:
        client = get_ollama_client(config)
        models = client.list().get("models", [])
        for m in models:
            if m.get("model") == model_name or m.get("name") == model_name:
                capabilities = m.get("capabilities", [])
                return capabilities if isinstance(capabilities, list) else []
        return []
    except Exception as e:
        logger.error(f"Failed to get capabilities for model '{model_name}': {e}")
        return []

def version(config) -> Optional[str]:
    """
    Return the Ollama server version.
    """
    try:
        client = get_ollama_client(config)
        return client.version()
    except Exception as e:
        logger.error(f"Failed to get Ollama server version: {e}")
        return None

def get_default_model(config) -> Optional[str]:
    """
    Return the default model configured on the Ollama server.
    """
    try:
        client = get_ollama_client(config)
        return getattr(client, "default_model", None)
    except Exception as e:
        logger.error(f"Failed to get default model: {e}")
        return None
