import pprint
from typing import Dict, List, Optional
from ollama import chat, Options
import logging

# Setup a standard logger
logger = logging.getLogger(__name__)

writing_tools = ['replacefile', 'replaceline', 'touch']

def send(user_text: str, messages: list, system_prompt: str, model: str, available_functions: Dict[str, any], options: Optional[Options] = None) ->  list:
    tools = list(available_functions.values())
    messages.append({"role": "user", "content": user_text})

    while True:
        print("\x1b[31mstart summaization\x1b[0m\n");
        messages = summarize_conversation(messages, system_prompt, model)
        pprint.pprint(f"\n[+] Context provided by assistant:\n{str(messages)}\n")
        print("\x1b[31mfinish summaization\x1b[0m\n");

        response: ChatResponse = chat(
            model=model,
            messages=messages,
            tools=tools,
            options=options
        )
        latest_prompt_eval_count = response.get('prompt_eval_count')
        print(f"Prompt tokens: {response.get('prompt_eval_count')}")
        print(f"Output tokens: {response.get('eval_count')}")
        if response.message.thinking is not None:
            print(f"Thinking: {response.message.thinking}")
        messages = process_tool_calls(response.message, available_functions, messages)

        if not response.message.tool_calls:
            print(f"{response.message.content}")
            break

def summarize_conversation(
        messages: list, 
        system_prompt: str, 
        model: str, 
        keep_recent_count: int = 5  # New parameter
        ) -> list:
    """
    Summarize the conversation history when it exceeds a certain limit.
    The last `keep_recent_count` messages will remain untouched and be appended 
    directly after the summary, while older messages are condensed.
    """
    print(f"number of messages: \x1b[34m{len(messages)}, {keep_recent_count}\x1b[0m\n");

    if len(messages) <= 2:
        return messages

    # 1. Separate the "Old" context from the "Recent" context
    # If keep_recent_count is 0 (default), the whole list (minus system) is summarized.
    if len(messages) > keep_recent_count:
        old_context = messages[:-keep_recent_count]
        new_context = messages[-keep_recent_count:]
    else:
        # If there aren't enough messages to fulfill the "keep" count, 
        # nothing needs summarizing.
        old_context = []
        new_context = messages

    # 2. Filter out system roles from the part being summarized
    summary_context = [m for m in old_context if m["role"] != "system"]

    # 3. Perform the summarization only on the older context
    summary_response = chat(
            model=model,
            messages=[
                {"role": "system", "content": "Summarize the following conversation briefly while retaining all key information and context. Do not include system instructions or persona details."},
                *summary_context
                ],
            )

    # 4. Construct the final list:
    # [System Prompt] + [Summary Result] + [Raw Recent Messages]
    final_history = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": f"Summary of previous conversation: {summary_response.message.content}"}
            ]

    # Add the messages that were supposed to stay untouched (skipping any systemic ones)
    for m in new_context:
        if m["role"] != "system":
            final_history.append(m)

    return final_history

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
