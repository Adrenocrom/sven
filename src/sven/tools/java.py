import subprocess

def maven_clean_install() -> dict:
    """
    Run Maven clean install and returns the status
    return:
        str: compilerwarnings and errors
    """
    try:
        result = subprocess.run(["mvn", "clean", "install"], capture_output=True, text=True)
        return {"success": True, "message": "OK", "data": result}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
