import subprocess

def touch(filename: str) -> None:
    """
    Create a file via touch

    Args:
        filename (str): The name of the file to be created.

    Returns:
        None
    """
    cmd = [ "touch", filename ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return
