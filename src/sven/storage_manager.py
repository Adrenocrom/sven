import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STATE_FILE = "state.json"

DEFAULT_STATE = {
    "user_settings": {
        "theme": "dark",
        "notifications": True
    },
    "current_progress": 0,
    "session_tokens": {}
}

def load_session():
    """
    Loads the session data from a JSON file.
    Returns default state if file is missing or corrupted.
    """
    if not os.path.exists(STATE_FILE):
        logger.info(f"{STATE_FILE} not found, using defaults.")
        return DEFAULT_STATE.copy()

    try:
        with open(STATE_FILE, 'r') as f:
            data = json.load(f)
            return data
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to load {STATE_FILE}: {e}. Falling back to defaults.")
        return DEFAULT_STATE.copy()

def save_session(data):
    """
    Saves the provided session data to a JSON file.
    """
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        logger.info(f"Session successfully saved to {STATE_FILE}.")
    except IOError as e:
        logger.error(f"Failed to save session to {STATE_FILE}: {e}")

if __name__ == "__main__":
    # Simple test
    state = load_session()
    print("Loaded state:", state)
    state["current_progress"] = 50
    save_session(state)
    print("Saved state.")
