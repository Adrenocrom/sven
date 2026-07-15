import subprocess

from sven.tools.security import validate_path

def add(filepath: str) -> dict:
    """
    does a git add

    args:
        str: filepath

    return:
        None
    """
    # Validate path is within project directory
    if not validate_path(filepath):
        return {"success": False, "message": f"Path {filepath} is outside the project directory.", "data": None}
    
    try:
        result = subprocess.run(["git", "add", filepath], capture_output=True, text=True)
        return {"success": True, "message": "OK", "data": result.stdout}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

def push() -> dict:
    """
    does a git push

    return:
        None
    """
    try:
        print("Pushing to remote...")
        result = subprocess.run(["git", "push"], capture_output=True, text=True)
        return {"success": True, "message": "OK", "data": result.stdout}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

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
        #push()
        return {"success": True, "message": "OK", "data": result.stdout}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

def diff() -> dict:
    """
    Do a git diff

    return:
        None
    """
    try:
        result = subprocess.run(["git", "diff"], capture_output=True, text=True)
        return {"success": True, "message": "OK", "data": result.stdout}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
