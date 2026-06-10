import subprocess

def autoformat(filepath: str) -> None:
    """
    autoformat the given file

    Args:
        filepath (str): The path of the file to format.

    Returns:
        None
    """
    cmd = [ "vim", "-Es", "+normal! gg=G", "+x", filepath ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return
