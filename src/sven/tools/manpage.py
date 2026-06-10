import subprocess

def manpage(programname: str) -> str:
    """
    Get the manual page for a program.

    Args:
        programname: The name of the program to get the manual page for.

    Returns:
        A string containing the manual page.
    """
    result = subprocess.run(["man", programname], capture_output=True, text=True)
    return result.stdout
