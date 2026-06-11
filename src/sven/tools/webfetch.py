import subprocess

def webfetch(url: str) -> dict:
    """Fetch content from a URL using curl.
    args:
        str: url
    """
    try:
        result = subprocess.run(["curl", "-L", url], capture_output=True, text=True)
        return {"success": True, "message": "OK", "data": result.stdout}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

