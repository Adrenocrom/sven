import subprocess

def read(filepath: str) -> str:
    """
    This function reads a file and prints its contents to the console.

    Args:
        filepath (str): The path of the file to be read.

    Returns:
        str: The contents of the file.
    """
    cmd = [ "cat", filepath ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return  result.stdout
