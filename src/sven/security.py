"""
Security utilities for path validation.

Provides functions to ensure file operations are restricted to the project directory.
"""

import os

# Project root directory - all file operations must be within this directory
PROJECT_ROOT = os.path.abspath(".")


def validate_path(filepath: str) -> bool:
    """
    Validate that a file path is within the project directory.

    This function resolves symlinks and relative paths to ensure the
    absolute path is within the project root.

    Args:
        filepath: The file path to validate. Can be absolute or relative.

    Returns:
        bool: True if the path is within the project directory, False otherwise.

    Examples:
        >>> validate_path("./test.txt")
        True
        >>> validate_path("../outside.txt")
        False
        >>> validate_path("/etc/passwd")
        False

    Note:
        Uses os.path.realpath() to resolve symlinks, preventing bypass attacks
        through symbolic links.
    """
    abs_path = os.path.realpath(filepath)
    return abs_path.startswith(PROJECT_ROOT)


def validate_paths(*paths: str) -> bool:
    """
    Validate that multiple file paths are within the project directory.

    Args:
        *paths: Variable number of file paths to validate.

    Returns:
        bool: True if all paths are within the project directory, False otherwise.

    Examples:
        >>> validate_paths("./file1.txt", "./file2.txt")
        True
        >>> validate_paths("./file1.txt", "../outside.txt")
        False
    """
    return all(validate_path(p) for p in paths)