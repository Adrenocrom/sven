import subprocess

def compilefiles() -> dict:
    """
    Compiles all python files and output the compiler warnings and errors.
    return:
        str: compilerwarnings and errors
    """
    try:
        result = subprocess.run(["find", ".", "-name", "*.py"], capture_output=True, text=True)
        files = result.stdout.split("\n")
        files.remove("")
        count = 1
        results = ""
        for file in files:
            result = subprocess.run(["poetry", "run", "python", "-m", "py_compile", file], capture_output=True, text=True)
            results += f"{file} - compiler output: {result.stdout}\n."
        return {"success": True, "message": "OK", "data": results}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
