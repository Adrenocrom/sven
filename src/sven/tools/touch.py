import subprocess

def touch(filepath: str) -> dict:
    """
    Create a file via touch
    """
    try:
        cmd = ["touch", filepath]
        result = subprocess.run(cmd, capture_output=True, text=True)
        # If exit code is 0, success.
        if result.returncode == 0:
            return {"success": True, "message": f'File {filepath} created.', "data": None}
        else:
            return {"success": False, "message": result.stderr or 'Unknown error', "data": None}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

