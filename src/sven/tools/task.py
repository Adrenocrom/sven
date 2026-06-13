"""
Module providing tools for managing a task queue using FIFO logic.
"""

from collections import deque
from typing import Optional
from sven.task_model import Task

# A global queue to store tasks internally during the session.
# In a production environment, this might be persisted in a database or file.
TASK_QUEUE = deque()

def add_task(description: str) -> dict:
    """
    Adds a new task with a generated ID to the FIFO queue.
    
    Args:
        description: A description of the task.
        
    Returns:
        A dictionary containing success status, message, and the new task ID.
    """
    import uuid
    task_id = str(uuid.uuid4())[:8]
    new_task = Task(id=task_id, description=description)
    TASK_QUEUE.append(new_task)
    return {"success": True, "message": "OK", "data": task_id}

def current_task() -> dict:
    """
    Returns the next task in the FIFO queue.
    
    Returns:
        A dictionary containing success status, message, and the Task data if available.
    """
    if not TASK_QUEUE:
        return {"success": False, "message": "No tasks in queue", "data": None}
    task = TASK_QUEUE[0]
    return {"success": True, "message": "OK", "data": task.to_dict()}

def cancel_task(task_id: str) -> dict:
    """
    Removes a specific task from the queue by its ID.
    
    Args:
        task_id: The unique identifier of the task to remove.
        
    Returns:
        A dictionary containing success status, message, and result.
    """
    for i, task in enumerate(TASK_QUEUE):
        if task.id == task_id:
            TASK_QUEUE.rotate(-i)
            TASK_QUEUE.popleft()
            TASK_QUEUE.rotate(i)
            return {"success": True, "message": "OK", "data": True}
    return {"success": False, "message": f"Task {task_id} not found", "data": False}

def complete_task() -> dict:
    """
    Marks the current task as completed by removing it from the front of the queue.
    
    Returns:
        A dictionary containing success status, message, and the Task data if available.
    """
    if not TASK_QUEUE:
        return {"success": False, "message": "No tasks to complete", "data": None}
    task = TASK_QUEUE.popleft()
    return {"success": True, "message": "OK", "data": task.to_dict()}
