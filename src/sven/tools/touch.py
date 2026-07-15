import subprocess

import os
import subprocess

from sven.tools import git

# Project root directory - all file operations must be within this directory
PROJECT_ROOT = os.path.abspath(".")

def validate_path(filepath: str) -> bool:
    """
    Validate that a file path is within the project directory.
    
    Args:
        filepath: The file path to validate
        
    Returns:
        bool: True if the path is within the project directory, False otherwise
    """
    abs_path = os.path.realpath(filepath)  # Resolve symlinks
    return abs_path.startswith(PROJECT_ROOT)

def touch(filepath: str) -> dict:
    """
    Create a file via touch
    """
    # Validate path is within project directory
    if not validate_path(filepath):
        return {"success": False, "message": f"Path {filepath} is outside the project directory.", "data": None}
    
    try:
        cmd = ["touch", filepath]
        result = subprocess.run(cmd, capture_output=True, text=True)
        # If exit code is 0, success.
        if result.returncode == 0:
            git.add(filepath)
            return {"success": True, "message": f'File {filepath} created.', "data": None}
        else:
            return {"success": False, "message": result.stderr or 'Unknown error', "data": None}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

