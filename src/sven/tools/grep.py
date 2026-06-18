"""Grep tool for Sven.

Provides a simple grep implementation using Python's regex engine.
All functions return a dict with keys: success (bool), message (str), data (any).
"""

import re
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
        regex = re.compile(pattern)
        matches: List[str] = []
        if not files:
            # Read from stdin
            for line in sys.stdin:
                if regex.search(line):
                    matches.append(line)
        else:
            for fname in files:
                try:
                    with open(fname, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if regex.search(line):
                                matches.append(f"{fname}:{line}")
                except FileNotFoundError:
                    return {"success": False, "message": f"File not found: {fname}", "data": None}
                except Exception as e:
                    return {"success": False, "message": str(e), "data": None}
        return {"success": True, "message": "OK", "data": "".join(matches)}
    except re.error as e:
        return {"success": False, "message": f"Invalid regex: {e}", "data": None}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
