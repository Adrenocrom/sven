"""
Security utilities for path validation.

Provides functions to ensure file operations are restricted to the project directory, with an optional user confirmation prompt when paths fall outside it.
"""

import os


class SecurityError(Exception):
    """Raised when a security check is rejected by the user."""
    pass


# Project root directory - all file operations must be within this directory
PROJECT_ROOT = os.path.abspath(".")


def validate_path(filepath: str) -> bool:
    """Validate that a file path is within the project directory.

    If the resolved absolute path falls outside PROJECT_ROOT, prompts the user to confirm whether they want to bypass the security check before proceeding. Symlinks are resolved via realpath() to prevent escape through symbolic links.

    Args:
        filepath: The file path to validate (absolute or relative).

    Returns:
        True if the path is within the project directory, or if the user confirms a one-time bypass for an out-of-directory path.

    Raises:
        SecurityError: If the path falls outside PROJECT_ROOT and the user rejects the bypass prompt.

    Examples:
        >>> validate_path("./test.txt")  # doctest: +SKIP
        True
        >>> validate_path("../outside.txt")  # doctest: +SKIP
        SecurityError(...) or True (depending on user input)
    """
    abs_path = os.path.realpath(filepath)

    normalized_root = os.path.normpath(PROJECT_ROOT).rstrip(os.sep)
    if not (abs_path == normalized_root or abs_path.startswith(normalized_root + os.sep)):
        print(
            f"⚠️  Security warning: '{filepath}' resolves outside the working directory "
            f"(current root: {PROJECT_ROOT}).\n"
        )
        response = input("Allow access? [y/N]: ").strip().lower()

        if response in ("y", "yes"):
            return True

        raise SecurityError(
            f"Bypass rejected by user. Refusing to operate on path outside project root: {filepath}"
        )

    return True


def validate_paths(*paths: str) -> bool:
    """Validate that multiple file paths are within the project directory.

    Each path is validated individually via :func:`validate_path`, which prompts the user for every out-of-directory path encountered (until one is rejected). If any call raises ``SecurityError``, it propagates immediately and subsequent paths are not checked.

    Args:
        *paths: Variable number of file paths to validate.

    Returns:
        True if all paths pass validation or the user confirms each bypass prompt.

    Raises:
        SecurityError: If any path is rejected by the user during a one-time bypass confirmation.

    Examples:
        >>> validate_paths("./file1.txt", "./file2.txt")  # doctest: +SKIP
        True
        >>> try:
        ...     validate_paths("./ok.txt", "../outside.txt")
        ... except SecurityError as e:
        ...     print(e)  # doctest: +SKIP
    """
    for path in paths:
        if not validate_path(path):
            return False

    return True


def get_project_root() -> str:
    """Return the absolute project root used by all security checks.

    Useful when callers need to display or log the enforced boundary, e.g. inside error messages.
    """
    return PROJECT_ROOT
