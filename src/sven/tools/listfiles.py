import subprocess

def listfiles() -> str:
    """
    List files in current directory
    Args:
        None
    Returns:
        list of files in the current directory
    """
    result = subprocess.run([ "find", "." ], capture_output=True, text=True)
    return
