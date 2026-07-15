"""Find file tool for Sven.

Provides a simple file‑search utility that walks a directory tree and returns
paths matching a glob pattern. All functions return a dict with the keys:
`success` (bool), `message` (str) and `data` (list of matching paths).
"""

import fnmatch
import os
from typing import List

from sven.security import validate_paths

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
    # Validate directory is within project directory
    if not validate_paths(directory):
        return {"success": False, "message": f"Directory {directory} is outside the project directory.", "data": None}
    
    try:
        if not os.path.isdir(directory):
            return {"success": False, "message": f"Not a directory: {directory}", "data": None}

        matches: List[str] = []
        if recursive:
            for root, dirs, filenames in os.walk(directory):
                # Remove 'target' and '.git' from the list that will be walked.
                # This mutates `dirs` in place → those sub‑directories are skipped.
                dirs[:] = [d for d in dirs if d not in {"target", ".git"}]

                # Filter filenames against the supplied pattern
                for filename in fnmatch.filter(filenames, pattern):
                    matches.append(os.path.join(root, filename))

        # ------------------------------------------------------------------
        # 2) Non‑recursive (just list the top‑level)
        # ------------------------------------------------------------------
        else:
            for entry in os.listdir(directory):
                # Skip directories that happen to be named 'target' or '.git'.
                if entry in {"target", ".git"}:
                    continue

                full_path = os.path.join(directory, entry)
                if os.path.isfile(full_path) and fnmatch.fnmatch(entry, pattern):
                    matches.append(full_path)

        return {"success": True, "message": "OK", "data": matches}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
