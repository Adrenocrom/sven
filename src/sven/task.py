"""
Module defining the Task data structure and logic for handling tasks.
"""

import json
from typing import List
from dataclasses import dataclass, asdict

@dataclass
class Task:
    id: str
    description: str
    success_defintion: str
    state: str
    plan: str
    raw_data: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        return cls(id=data['id'], success_defintion = data['success_defintion'], state=data['state'], description=data['description'], plan=data['plan'], raw_data=data['raw_data'])

def load_tasks_from_json(filepath: str) -> List[Task]:
    """
    Loads a list of Task objects from a JSON file.
    
    Args:
        filepath: Path to the JSON file.
        
    Returns:
        A list of Task instances.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return [Task.from_dict(item) for item in data]
            else:
                raise ValueError("JSON content must be a list of tasks.")
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
        return []
    except Exception as e:
        print(f"Error loading tasks from {filepath}: {e}")
        return []

def save_tasks_to_json(tasks: List[Task], filepath: str) -> None:
    """
    Saves a list of Task objects to a JSON file.
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump([t.to_dict() for t in tasks], f, indent=2)
