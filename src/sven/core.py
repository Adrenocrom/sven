import pprint
from typing import Dict, List, Optional
from ollama import chat, Options
import logging

from sven.tools.task import add_task, current_task, cancel_task, complete_task, list_tasks

task_functions = {
  'add_task': add_task,
  'current_task': current_task,
  'list_tasks': list_tasks,
  'cancel_task': cancel_task,
  'complete_task': complete_task,
}

# Setup a standard logger
logger = logging.getLogger(__name__)

writing_tools = ['replacefile', 'replaceline', 'touch']

def send(user_text: str, messages: list, system_prompt: str, model: str, available_functions: Dict[str, any], options: Optional[Options] = None) ->  list:
    tools = list(available_functions.values())

    messages.append({"role": "user", "content": user_text})

    while True:
        print("\x1b[31mstart summaization\x1b[0m\n");
        messages = generate_mission_brief(messages, tools, system_prompt, model)
        pprint.pprint(messages)
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
            print(f"Thinking: \x1b[33m{response.message.thinking}\x1b[0m")
        messages = process_tool_calls(response.message, available_functions, messages)

        if not response.message.tool_calls:
            print(f"{response.message.content}")
            break

def generate_mission_brief(messages: list, tools: list, system_prompt: str, model: str) -> list:
    """
    Analyzes the conversation context and a provided list of available capabilities 
    to generate a specialized System Prompt for the next stage.
    """
    task_tools = list(task_functions.values())

    # Filter out existing system prompts from the history to keep focus on user/assistant interaction
    summary_context = [m for m in messages if m["role"] != "system"]

    # Convert the tools list into a formatted string for the prompt instructions.
    # This ensures the LLM reads them as capabilities rather than technical definitions.
    tools_description = "\n".join([f"- {t}" for t in tools])

    meta_instruction = f"""
    You are a State Preservation Engine. You act as a high-fidelity bridge between 
    the current interaction and the next execution step. Your goal is to ensure 
    that NO technical data, unique identifiers, or raw values from tool outputs 
    are lost during transition.

    You will be provided with a conversation transcript and a list of available capabilities:
    {tools_description}

    Your task is to generate a "State & Data Payload." You must act as a data-router: 
    preserve the full depth of the technical state while identifying the next logical step.

    Use the inbuild task system!

    The Payload must include:

    1. **Primary Objective**: A clear statement of the user's ultimate goal.
    2. **Raw Data Repository**: Capture and list ALL persistent values, including 
       but not limited to: unique IDs (e.g., UUIDs, order_ids), exact prices, 
       dates/timestamps, contact info, and full JSON objects returned by tools 
       that contain data needed for future steps. Do NOT simplify or summarize these.
    3. **Execution Trace**: A verbatim log of the most recent tool call result. 
       Include the raw output to ensure any specific "success" flags or 
       variable values are available for the next step.
    4. **Validation Status**: Identify if any information is currently missing or 
       if a tool recently returned an error/warning that requires specific 
       handling in the next turn.
    5. **Next Step Logic**: A specific instruction for the execution agent. 
       State exactly which tool to call and provide the specific values from the 
       "Raw Data Repository" to be used as arguments.

    Constraints:
    - DATA INTEGRITY: Do not summarize or shorten data strings, ID numbers, or JSON objects.
    - NO CONVERSATION: Do not include any pleasantries, meta-commentary, or filler text.
    - NO BREVITY: It is better to have a long, detailed Payload than a short, incomplete one. 
      If the tool output was long, keep the relevant parts of it.
    - OUTPUT ONLY the State & Data Payload.
    """

    history = [
            {"role": "system", "content": meta_instruction},
            *summary_context
        ]
    while True:
        response = chat(
            model=model,
            tools=task_tools,
            messages=history
        )
        history = process_tool_calls(response.message, task_functions, messages)
        if not response.message.tool_calls:
            return [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": response.message.content}
            ]

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
