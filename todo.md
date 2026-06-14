# Project TODO List

## Current Task
- [ ] Implement Robust Error Handling for Tool Calls: Standardize the return type of all tools and add more granular error handling in core.py.

## Plan
1. Analyze `src/sven/tools` to identify current tool return types.
2. Define a standard response structure (e.g., a dataclass or a consistent dictionary) for all tool outputs.
3. Update each tool implementation in `src/sven/tools/*.py` to return this standardized format.
4. Modify `src/sven/core.py` to handle these responses and provide specific error messages based on the new structure.
5. Add logging or detailed exception handling for common failure modes (e.g., network errors, file not found).
6. Verify all tools still function correctly with the new interface.