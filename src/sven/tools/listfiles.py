import subprocess

def listfiles() -> dict:
    """
    List files in current directory
    """
    try:
        result = subprocess.run(["find", "."], capture_output=True, text=True)
        return {"success": True, "message": "OK", "data": result.stdout}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

