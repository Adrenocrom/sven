import subprocess

def autoformat(filename: str) -> None:
    """
    autoformat the given file

    Args:
        filename (str): The name of the file to format.

    Returns:
        None
    """
    cmd = [ "vim", "-Es", "+normal! gg=G", "+x", filename ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return
