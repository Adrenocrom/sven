import subprocess

def read(filepath: str, offset: int = 0) -> dict:
    """
    Read the content of a file.
    Max size of the data is 2048 bytes, based on the offset.

    args:
        str: filepath
        int: offset (default is 0)

    returns:
        dict: success status, message, and data
    """
    max_size = 2048

    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            file.seek(offset)
            data = file.read(max_size)
        return {"success": True, "message": "OK", "data": data}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

