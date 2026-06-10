import subprocess

def listfiles() -> str:
    """list files in current directory"""
    """
    Returns:
        list of files in the current directory
    """
    result = subprocess.run([ "find", "." ], capture_output=True, text=True)
    return
