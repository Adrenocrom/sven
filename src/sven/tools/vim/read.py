import subprocess

def read(filename: str) -> str:
    """
    This function reads a file and prints its contents to the console.

    Args:
        filename (str): The name of the file to be read.

    Returns:
        str: The contents of the file.
    """
    cmd = [ "cat", filename ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return  result.stdout
