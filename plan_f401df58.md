# Implementation Plan: Multi-Step Task Planning (Task f401df58)

## Objective
Implement a "Plan" mode where the system can decompose complex user requests into a sequence of discrete tasks, store them in a queue, and execute them one by one until completion.

## Current State Analysis
- Existing tools: `add_task`, `current_task`, `list_tasks`, `complete_task`.
- These tools already provide the infrastructure for a task queue.
- The current flow is linear (one prompt -> one tool call or response).

## Proposed Architecture Changes

### 1. Planning Logic (Internal Reasoning)
When a user provides a complex request, Sven should:
- Detect that multiple steps are required.
- Generate a structured plan (a list of clear, actionable sub-tasks).
- Present this plan to the user for confirmation (optional but recommended for UX).

### 2. Task Queue Integration
Instead of executing a large multi-step process in one go:
1.  **Plan Generation**: Sven generates $N$ steps.
2.  **Queue Population**: For each step, call `add_task(description=...)`.
3.  **Execution Loop**: 
    - Fetch `current_task()`.
    - Determine the necessary tool(s) to fulfill that specific task's description.
    - Execute the tool.
    - Call `complete_task()` upon success.
    - Repeat until no tasks remain or a failure occurs.

### 3. System Prompt Update
Update the system instructions to:
- Explicitly define "Planning Mode".
- Instruct Sven to use the task tools when a request involves multiple distinct operations (e.g., "Refactor this class and then update all imports").
- Provide guidance on how to write concise, actionable descriptions for `add_task`.

### 4. Implementation Steps

#### Phase 1: Infrastructure & Logic
- [ ] Modify the core loop to check if a task exists in the queue before processing a standard prompt.
- [ ] Create a "Planner" helper or logic block that parses a user's request into a list of strings (tasks).
- [ ] Implement an automatic transition: If `add_task` is called, the next cycle should automatically fetch and attempt to complete the task.

#### Phase 2: UI/UX Enhancements
- [ ] Add status indicators for multi-step tasks (e.g., "Step 3 of 5: Updating configuration").
- [ ] Provide a summary of the plan before starting execution.

#### Phase 3: Error Handling & Recovery
- [ ] If a step fails, the system should report the error and ask the user for clarification/correction before attempting to proceed or retry that specific step.
- [ ] Implement "Retry" logic for transient failures (e.g., network issues during web search).

#### Phase 4: Testing
- [ ] Create test cases with complex requirements (e.g., "Find a library, install it, and write a sample script").
- [ ] Verify that the task queue persists correctly across turns if needed.
- [ ] Ensure `complete_task` is only called when the specific sub-goal of that step is met.

## Technical Details
- **State Management**: The state should be managed by the presence of items in the task list. If `list_tasks()` returns a non-empty list, the system enters "Execution Mode".
- **Prompting Strategy**: Use a two-pass approach for complex requests: 1) Planning Pass (LLM generates the plan), 2) Execution Pass (System follows the queue).
-