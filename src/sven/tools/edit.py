import subprocess

from sven.tools import git

def searchandreplace(filepath: str, oldcontent: str, newcontent: str) -> dict:
    """
    replaces old content with new content

    args:
        str: filepath
        str: oldcontent
        str: newcontent
    return:
        dict: result of the operation
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = file.read()
        new_data = data.replace(oldcontent, newcontent)
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(new_data)

        return {"success": True, "message": "OK", "data": None}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

def replacefile(filepath: str, newcontent: str) -> dict:
    """
    Replace the whole file with new content.
    If the file does not exists, a new file is created.
    
    args:
        str: filepath
        str: newcontent
    return:
        dict: result of the operation
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(newcontent)
        return {"success": True, "message": "OK", "data": None}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

def replaceline(filepath: str, linenumber: int, newcontent: str) -> dict:
    """
    Replace a line in a file with new content.
    
    args:
        str: filepath
        int: linenumber
        str: newcontent
    return:
        dict: result of the operation
    """
    try:
        vimmacro = f"gg{linenumber}cc{newcontent}"
        cmd = ["vim", "-Es", f"+normal! {vimmacro}", "+x", filepath]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return {"success": True, "message": "OK", "data": None}
        else:
            return {"success": False, "message": f"Vim command failed with code {result.returncode}", "data": result.stderr}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

