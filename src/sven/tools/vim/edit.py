import subprocess

def searchandreplace(filename: str, pattern ,newcontent: str) -> None:
    """
    Search a pattern and replace it with new content

    Args:
        filename (str): The name of the file to modify.
        pattern (str): Searchpattern
        newcontent (str): The new content for replace.

    Returns:
        None
    """
    vimcmd = f"%s/{pattern}/{newcontent}/g"
    cmd = [ "vim", "-Es", f"+normal! {vimcmd}", "+x", filename ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return

def replacefile(filename: str, newcontent: str) -> None:
    """
    Replace the hole file with new content.

    Args:
        filename (str): The name of the file to modify.
        newcontent (str): The new content for the specified line.

    Returns:
        None
    """
    vimmacro = f"ggVGc{newcontent}"
    cmd = [ "vim", "-Es", f"+normal! {vimmacro}", "+x", filename ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return

def replaceline(filename: str, linenumber: int, newcontent: str) -> None:
    """
    Replace a line in a file with new content.

    Args:
        filename (str): The name of the file to modify.
        linenumber (int): The line number in the file to replace.
        newcontent (str): The new content for the specified line.

    Returns:
        None
    """
    vimmacro = f"gg{linenumber}cc{newcontent}"
    cmd = [ "vim", "-Es", f"+normal! {vimmacro}", "+x", filename ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return
