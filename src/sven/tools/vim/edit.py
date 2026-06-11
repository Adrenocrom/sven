import subprocess

def searchandreplace(filepath: str, pattern: str) -> dict:
    """
    Search a pattern and replace it with new content.
    Example pattern: /test/replaced/g

    args:
        str: filepath
        str: pattern
    return:
        dict: result of the operation
    """
    try:
        vimcmd = f"%s{pattern}"
        cmd = ["vim", "-Es", f"+normal! {vimcmd}", "+x", filepath]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return {"success": True, "message": "OK", "data": None}
        else:
            return {"success": False, "message": f"Vim command failed with code {result.returncode}", "data": result.stderr}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

def replacefile(filepath: str, newcontent: str) -> dict:
    """
    Replace the whole file with new content.
    
    args:
        str: filepath
        str: newcontent
    return:
        dict: result of the operation
    """
    try:
        vimmacro = f"ggVGc{newcontent}"
        cmd = ["vim", "-Es", f"+normal! {vimmacro}", "+x", filepath]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return {"success": True, "message": "OK", "data": None}
        else:
            return {"success": False, "message": f"Vim command failed with code {result.returncode}", "data": result.stderr}
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

