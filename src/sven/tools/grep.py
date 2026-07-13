"""Grep tool for Sven.

Provides a wrapper around the system grep utility using the subprocess module.
All functions return a dict with keys: success (bool), message (str), data (any).
"""

import subprocess
import sys
from typing import List, Optional

def grep(pattern: str, files: Optional[List[str]] = None) -> dict:
    """Search for a regex pattern in given files or stdin.

    Args:
        pattern: Regular expression pattern to search for.
        files: List of file paths. If None or empty, reads from stdin.

    Returns:
        dict: {"success": bool, "message": str, "data": str}
        "data" contains the matching lines, each terminated with a newline.
    """
    try:
        # Construct the command: 'grep' + pattern + files (if any)
        # We use -H to ensure filename is printed even if only one file is provided
        command = ["grep", "-rni", pattern]
        
        if files:
            command.extend(files)
        
        # Execute the subprocess
        # stdin=sys.stdin allows the subprocess to read from stdin if no files are provided
        result = subprocess.run(
            command,
            input=None, 
            capture_output=True,
            text=True,
            stdin=sys.stdin if not files else None
        )

        # Grep exit codes: 0 = matches found, 1 = no matches, 2 = error
        if result.returncode == 0:
            return {"success": True, "message": "OK", "data": result.stdout}
        elif result.returncode == 1:
            return {"success": True, "message": "No matches found", "data": ""}
        else:
            return {"success": False, "message": result.stderr.strip() or "Grep error", "data": None}

    except FileNotFoundError:
        return {"success": False, "message": "grep command not found on system", "data": None}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
