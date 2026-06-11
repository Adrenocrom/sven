import subprocess

def read(filepath: str) -> dict:
    """
    Read the content of a file.
    """
    try:
        result = subprocess.run(["cat", filepath], capture_output=True, text=True)
        return {"success": True, "message": "OK", "data": result.stdout}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

