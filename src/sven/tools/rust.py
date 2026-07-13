import subprocess

def cargoBuild() -> dict:
    """
    cargo build and output the compiler warnings and errors.
    return:
        str: compilerwarnings and errors
    """
    try:
        result = subprocess.run(["cargo", "build"], capture_output=True, text=True)
        return {"success": True, "message": "OK", "data": result.stdout}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
