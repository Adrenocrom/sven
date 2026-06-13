"""
Module providing tools for managing a task queue using FIFO logic.
"""

from collections import deque
from typing import Optional
from src.sven.task_model import Task

# A global queue to store tasks internally during the session.
# In a production environment, this might be persisted in a database or file.
TASK_QUEUE = deque()

def add_task(description: str) -> str:
    """
    Adds a new task with a generated ID to the FIFO queue.
    
    Args:
        description: A description of the task.
        
    Returns:
        The unique identifier for the newly created task.
    """
    import uuid
    task_id = str(uuid.uuid4())[:8]
    new_task = Task(id=task_id, description=description)
    TASK_QUEUE.append(new_task)
    return task_id

def current_task() -> Optional[Task]:
    """
    Returns the next task in the FIFO queue.
    
    Returns:
        The current Task object if available, otherwise None.
    """
    if not TASK_QUEUE:
        return None
    return TASK_QUEUE[0]

def cancel_task(task_id: str) -> bool:
    """
    Removes a specific task from the queue by its ID.
    
    Args:
        task_id: The unique identifier of the task to remove.
        
    Returns:
        True if the task was found and removed, False otherwise.
    """
    for i, task in enumerate(TASK_QUEUE):
        if task.id == task_id:
            TASK_QUEUE.rotate(-i)
            TASK_QUEUE.popleft()
            TASK_QUEUE.rotate(i)
            return True
    return False

def complete_task() -> Optional[Task]:
    """
    Marks the current task as completed by removing it from the front of the queue.
    
    Returns:
        The Task object that was completed, or None if the queue was empty.
    """
    if not TASK_QUEUE:
        return None
    return TASK_QUEUE.popleft()
