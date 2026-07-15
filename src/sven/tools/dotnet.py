import subprocess

def dotnet_build() -> dict:
    """
    Return a list of error and warnings emitted on building the application using .NET.
    return:
        str: compilerwarnings and errors
    """
    try:
        result = subprocess.run(["dotnet", "build"], capture_output=True, text=True)
        return {"success": True, "message": "OK", "data": result}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
