import pprint
from typing import Dict, List, Optional
from ollama import chat, Options
import logging

# Setup a standard logger
logger = logging.getLogger(__name__)

writing_tools = ['replacefile', 'replaceline', 'touch']

def send(user_text: str, messages: list, system_prompt: str, model: str, available_functions: Dict[str, any]) ->  list:
    tools = list(available_functions.values())
    if len(messages) > 1:
        messages = summarize_conversation(messages, system_prompt, model) # Note: you might need to pass 'model' if it varies
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
        messages = process_tool_calls(response.message, available_functions, messages)

        if not response.message.tool_calls:
            print(f"\x1b[31mSven\033[0m: {response.message.content}")
            break

def summarize_conversation(messages: list, system_prompt: str, model: str) -> list:
    """
    Summarize the conversation history when it exceeds a certain limit.
    Returns a new message list containing the system prompt followed by the summary.
    """
    summary_context = [m for m in messages if m["role"] != "system"]
    summary_response = chat(
        model=model,
        messages=[
            {"role": "system", "content": "Summarize the following conversation briefly while retaining all key information and context. Do not include system instructions or persona details."},
            *summary_context
        ],
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": f"Summary of previous conversation: {summary_response.message.content}"}
    ]

def process_tool_calls(
        response_message, 
        available_functions: Dict[str, any], 
        messages: list
        ) -> list:
    """
    Process tool calls from a model response.

    Args:
        response_message: The message object returned by the Ollama client.
        available_functions: A map of function names to actual python callables.
        messages: The current conversation history (list of dicts).

    Returns:
        The updated message list after processing tool calls.
    """
    if not response_message.tool_calls:
        messages.append({
                'role': 'assistant',
                'content': response_message.content,
            })
        return messages

    # Append the original model's response first
    messages.append({
            'role': 'assistant',
            'tool_calls': response_message.tool_calls,
        })

    for tc in response_message.tool_calls:
        func_name = tc.function.name
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
            if result.get("success"):
                content = result.get("data") if result.get("data") is not None else ""
                logger.debug(f"Tool '{func_name}' executed successfully.")
            else:
                error_msg = result.get('message', 'Unknown error')
                logger.warning(f"Tool '{func_name}' failed with logic error: {error_msg}")
                content = f"Error: {error_msg}"

            messages.append({
                "role": "tool", 
                "tool_name": func_name, 
                "content": str(content)
                })

        except Exception as e:
            logger.exception(f"Exception occurred while handling tool '{func_name}': {str(e)}")
            content = f"Error: {str(e)}"
            messages.append({
                "role": "tool", 
                "tool_name": func_name, 
                "content": str(content)
                })
    return messages
