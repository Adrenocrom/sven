import subprocess

def read(filepath: str, offset: int = 0, length: int = 1000) -> dict:
    """
    Read a portion of the content of a file.

    args:
        filepath (str): The path to the file.
        offset (int): The starting position in bytes from which to read. Defaults to 0.
        length (int): The number of bytes to read. If -1, reads until end of file. Defauls to 1000

    returns:
        dict: A dictionary containing the success status, message, and data.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            # Move the cursor to the specified offset
            file.seek(offset)
            
            # If length is -1, it reads until the end of the file
            if length == -1:
                data = file.read()
            else:
                data = file.read(length)
                
        return {"success": True, "message": "OK", "data": data}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
