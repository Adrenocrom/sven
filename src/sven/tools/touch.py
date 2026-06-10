import subprocess

def touch(filepath: str) -> None:
    """
    Create a file via touch

    Args:
        filepath (str): The name/path of the file to be created.

    Returns:
        None
    """
    cmd = [ "touch", filepath ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return
