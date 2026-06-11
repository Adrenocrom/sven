import subprocess

def commit(message: str) -> dict:
    """
    does a git commit

    args:
        str: message
    return:
        None
    """
    try:
        print(f"Commiting: {message}")
        result = subprocess.run(["git", "commit", "-am", message], capture_output=True, text=True)
        return {"success": True, "message": "OK", "data": result.stdout}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
