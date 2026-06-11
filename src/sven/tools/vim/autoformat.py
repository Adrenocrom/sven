import subprocess

def autoformat(filepath: str) -> dict:
    """
    Automatically format a file using vim's formatting tools.
    
    Args:
        filepath (str): Path to the file to be formatted.
        
    Returns:
        dict: Success status and message or data.
    """
    try:
        # Using -es (silent, script) for clean execution in non-interactive mode
        cmd = ["vim", "-Es", f"+%s", "+x", filepath]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return {"success": True, "message": "OK", "data": None}
        else:
            return {"success": False, "message": f"Autoformat failed with code {result.returncode}", "data": result.stderr}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

