import subprocess

def manpage(programname: str) -> dict:
    """
    Get the manual page for a program.
    """
    try:
        result = subprocess.run(["man", programname], capture_output=True, text=True)
        return {"success": True, "message": "OK", "data": result.stdout}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

