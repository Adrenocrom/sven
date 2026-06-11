import subprocess

def websearch(query: str) -> dict:
    """Search web via duckduckgo"""
    try:
        result = subprocess.run(["ddgr", "--noprompt", query], capture_output=True, text=True)
        return {"success": True, "message": "OK", "data": result.stdout}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

