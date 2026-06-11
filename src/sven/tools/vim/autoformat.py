import subprocess

def autoformat(filepath: str) -> dict:
    """
    Auto format file using vim's formatting.
    """
    try:
        cmd = ["vim", "-Es", "+normal! gqG", "+x", filepath]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {"success": True, "message": "OK", "data": None}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

