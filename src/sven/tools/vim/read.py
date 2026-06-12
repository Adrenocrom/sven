import subprocess

def read(filepath: str) -> dict:
    """
    Read the content of a file.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = file.read()
        return {"success": True, "message": "OK", "data": data}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

