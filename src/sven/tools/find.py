"""Find file tool for Sven.

Provides a simple file‑search utility that walks a directory tree and returns
paths matching a glob pattern. All functions return a dict with the keys:
`success` (bool), `message` (str) and `data` (list of matching paths).
"""

import os
import fnmatch
from typing import List

def find(pattern: str, directory: str = ".", recursive: bool = True) -> dict:
    """Search for files whose names match *pattern*.

    Args:
        pattern: Unix shell‑style wildcard pattern (e.g. "*.py").
        directory: Root directory to start the search (default: current directory).
        recursive: If True, descend into sub‑directories.

    Returns:
        dict: {
            "success": bool,
            "message": str,
            "data": List[str] | None
        }
        `data` contains the list of matching file paths relative to *directory*.
    """
    try:
        if not os.path.isdir(directory):
            return {"success": False, "message": f"Not a directory: {directory}", "data": None}

        matches: List[str] = []
        if recursive:
            for root, _, filenames in os.walk(directory):
                for filename in fnmatch.filter(filenames, pattern):
                    matches.append(os.path.join(root, filename))
        else:
            for entry in os.listdir(directory):
                full_path = os.path.join(directory, entry)
                if os.path.isfile(full_path) and fnmatch.fnmatch(entry, pattern):
                    matches.append(full_path)

        return {"success": True, "message": "OK", "data": matches}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
