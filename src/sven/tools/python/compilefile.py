import subprocess

def compilefile(filepath: str) -> dict:
    """
    Compiles the file and output the compiler warnings.

    args:
        str: filepath
    return:
        str: compilerwarnings and errors
    """
    try:
        result = subprocess.run(["poetry", "run", "python", "-m", "py_compile", filepath], capture_output=True, text=True)
        return {"success": True, "message": "OK", "data": result.stdout}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
