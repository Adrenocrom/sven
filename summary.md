# Analysis of Token Growth and Contextual Filtering

## Current Problem
The program's context window grows linearly with every interaction because the `messages` list in `src/sven/chat.py` appends all user inputs, assistant responses, and raw tool outputs (which can be very large for operations like `read` or `webfetch`). This leads to a "token growth" issue where eventually the model will hit its context limit.

## Findings
- **`src/sven/chat.py`**: The list `messages` is passed directly to the LLM in every loop iteration.
- **`src/sven/core_logic.py`**: Tool results are appended as strings. If a tool returns a large file or long web page, it consumes significant tokens immediately.

## Proposed Solution: Contextual Filtering
To implement contextual filtering and mitigate token growth, the following strategies should be applied in `src/sven/core_logic.py`:

1. **Truncation / Summarization**: Instead of appending the raw content from a tool (e.g., `read`), only append relevant snippets or summarize the output if it exceeds a certain threshold.
2. **Contextual Relevance**: Filter out intermediate "system" logs or redundant information that doesn't provide semantic value for subsequent turns.
3. **Rolling Window / Buffer**: Implement a sliding window where only the last $N$ messages (or the most recent relevant history) are sent to the LLM, while keeping a summarized state of previous tasks.
4. **Tool-Specific Filtering**: 
   - For `read`, if the file is large, extract only lines surrounding the modified area or specific requested information.
   - For `webfetch`, parse the HTML and send only the core text/content instead of the full raw response.

## Recommendation
Refactor `process_tool_calls` in `src/sven/core_logic.py` to include a filtering layer that evaluates the size of `result.get("data")` and summarizes or clips it before adding it to the `messages` list.