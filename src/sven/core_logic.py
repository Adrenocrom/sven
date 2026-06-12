from typing import Dict, List, Optional

wrinting_tools = [  'replacefile', 'replaceline', 'touch' ]
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
            'role': ' assistant',
            'tool_calls': response_message.tool_calls,
        })

    for tc in response_message.tool_calls:
        func_name = tc.function.name
        if func_name in available_functions:
            if func_name in wrinting_tools:
                print(f"\x1b[32mtoolcall {func_name} with arguments {tc.function.arguments}\x1b[0m")
            else:
                print(f"\x1b[34mtoolcall {func_name} with arguments {tc.function.arguments}\x1b[0m")

            try:
                result = available_functions[func_name](**tc.function.arguments)
                if result.get("success"):
                    content = result.get("data") if result.get("data") is not None else ""
                else:
                    content = f"Error: {result.get('message')}"
                messages.append({
                    "role": "tool", 
                    "tool_name": func_name, 
                    "content": str(content)
                    })

            except Exception as e:
                content = f"Error: {str(e)}"
                messages.append({
                    "role": "tool", 
                    "tool_name": func_name, 
                    "content": str(content)
                    })
    return messages

