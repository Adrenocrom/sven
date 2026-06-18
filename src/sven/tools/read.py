import subprocess

def read(filepath: str, offset: int = 0, length: int = 1000) -> dict:
    """
    Read a portion of the content of a file based on line numbers (line-offset based).

    NOTE: The parameters 'offset' and 'length' now refer to lines, not bytes.

    args:
        filepath (str): The path to the file.
        offset (int): The starting line number (1-indexed). Defaults to 0 (will read from line 1).
        length (int): The maximum number of lines to read. If -1, reads until end of file. Defaults to 1000.

    returns:
        dict: A dictionary containing the success status, message, and data.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            # Treat offset=0 as starting from line 1 for user convenience
            start_line = max(1, offset)
            
            lines = []
            current_line = 0
            
            # 1. Skip to the starting line (offset)
            while current_line < start_line:
                line = file.readline()
                if not line:
                    break # EOF reached before starting line
                current_line += 1

            # 2. Read up to 'length' lines from the starting point
            lines_to_read = length if length != -1 else float('inf')
            
            while current_line < start_line + lines_to_read:
                line = file.readline()
                if not line:
                    break # EOF reached
                lines.append(line)
                current_line += 1

            data = "".join(lines)
                
        return {"success": True, "message": "OK", "data": data}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}