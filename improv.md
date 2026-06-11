# Improvement Roadmap for Sven

## Current Progress
- [x] **Consistent Tool Interfaces**: All tools now share a unified response schema (`success`, `message`, `data`), enabling consistent interaction between the core logic and the LLM.
- [x] **Basic Error Handling**: Individual tool implementations are wrapped in try/except blocks to ensure that system errors are caught and communicated back as "failures" rather than crashing the loop.

## Upcoming Improvements

### 1. Advanced Tool Validation
- Implement more rigorous validation of `tool_call` arguments before execution (e.g., type casting for numbers, presence of required strings).
- Provide specific feedback to the model when a call is malformed so it can self-correct.

### 2. Enhanced Editing Logic
- **Large File Handling**: Move away from full-file replacement for very large files, implementing chunked reading/writing or targeted line editing.
- **Escaping & Safety**: Implement better escaping of special characters in `newcontent` to ensure that multi-line inputs do not break Vim's command processing.

### 3. Performance & Scalability
- **Result Caching**: Cache results for repetitive operations (e.g., `websearch` or `getdatetime`) within the context of a single session.
- **Asynchronous I/O**: Implement `asyncio` for non-blocking file system interactions and network requests.

### 4. User Experience & DX
- **Progressive CLI Tools**: Add flags for `--model`, `--temperature`, and `--verbose`.
- **Auto-Generated Documentation**: Generate a help menu or local "man" page that dynamically lists all available tools and their required parameters for the LLM to reference.

### 5. Integration
- Provide hooks for deeper integration with IDEs (VSCode/Neovim) as backend drivers rather than just a standalone CLI shell.

