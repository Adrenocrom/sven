import subprocess

def webfetch(url: str) -> dict:
    """Fetch content from a URL using curl.
    args:
        str: url
    """
    try:
        result = subprocess.run(["web_fetch", url], capture_output=True, text=True)
        if result.returncode == 0:
            return {"success": True, "message": "OK", "data": result.stdout}
        else:
            return {"success": False, "message": f"Curl failed with exit code {result.returncode}", "data": result.stderr}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

