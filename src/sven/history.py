import json
from pathlib import Path

def load_history() -> list[str]:
    try:
        file_path = Path('history.json')
        if not file_path.exists():
            return []
        with open(file_path, 'r') as file:
            history = json.load(file)
        return history
    except Exception as e:
        print(f"Error loading history: {e}")
        return []

def store_history(history: list[str]):
    try:
        final_history = [m for m in history if not m.get('tool_calls')] 
        file_path = Path('history.json')
        with open(file_path, 'w') as file:
            json.dump(final_history, file, indent=4)
    except Exception as e:
        print(history)
        print(f"Error storing history: {e}")

