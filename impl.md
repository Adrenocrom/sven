# Implementation Plan: Contextual Filtering

## Objective
Mitigate token growth in the conversation context by filtering and summarizing tool outputs before they are added to the message history.

## Tasks

### 1. Refactor `process_tool_calls` in `src/sven/core.py`
- Implement a filtering layer for the `result.get("data")`.
- For large results (e.g., from the `read` tool), implement logic to:
    - Check result length.
    - If above a threshold (e.g., 2000 characters), truncate or summarize.
- Filter out redundant system logs/noise.

### 2. Tool-Specific Logic (Internal to core)
- **`read` tool:** If the output is large, only keep relevant segments if possible (though initial focus is on general length truncation).
- Note: Skip `webfetch` logic as it will be handled separately.

## Technical Details
- Target file: `src/sven/core.py`
- Threshold for "large" content: 2048 characters (configurable).
- Replacement strategy: If content > threshold, append a notice: "[Content truncated due to size]".
