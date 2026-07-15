import subprocess
import shutil

from sven.tools import git
from sven.security import validate_path

def searchandreplace(filepath: str, oldcontent: str, newcontent: str) -> dict:
    """
    replaces old content with new content

    args:
        str: filepath
        str: oldcontent
        str: newcontent
    return:
        dict: result of the operation
    """
    # Validate path is within project directory
    if not validate_path(filepath):
        return {"success": False, "message": f"Path {filepath} is outside the project directory.", "data": None}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = file.read()
        new_data = data.replace(oldcontent, newcontent)
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(new_data)

        return {"success": True, "message": "OK", "data": None}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

def replacefile(filepath: str, newcontent: str) -> dict:
    """
    Replace the whole file with new content.
    If the directory does not exist, it is created.
    If the file does not exists, a new file is created.
    
    args:
        str: filepath
        str: newcontent
    return:
        dict: result of the operation
    """
    # Validate path is within project directory
    if not validate_path(filepath):
        return {"success": False, "message": f"Path {filepath} is outside the project directory.", "data": None}
    
    try:
        # Get the directory path from the filepath
        directory = os.path.dirname(filepath)
        
        # Create directory if it doesn't exist (and isn't the current root)
        if directory:
            os.makedirs(directory, exist_ok=True)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(newcontent)
        return {"success": True, "message": "OK", "data": None}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

def replaceline(filepath: str, linenumber: int, newcontent: str) -> dict:
    """
    Replace a line in a file with new content using standard file I/O.
    This avoids external dependencies like vim or subprocess.
    
    args:
        str: filepath
        int: linenumber (1-indexed)
        str: newcontent
    return:
        dict: result of the operation
    """
    # Validate path is within project directory
    if not validate_path(filepath):
        return {"success": False, "message": f"Path {filepath} is outside the project directory.", "data": None}
    
    try:
        # 1. Read all lines into memory
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Check if the line number is valid (linenumber is 1-indexed)
        if not (1 <= linenumber <= len(lines)):
            return {"success": False, "message": f"Line {linenumber} does not exist in {filepath}.", "data": None}

        # 2. Modify the specific line (list indices are 0-based)
        # We must ensure the new content includes a newline character if it's meant to replace a full line.
        lines[linenumber - 1] = newcontent + '\n'

        # 3. Write all modified lines back to the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return {"success": True, "message": "Successfully replaced line content.", "data": None}

    except FileNotFoundError:
        return {"success": False, "message": f"File not found at {filepath}.", "data": None}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

def move_file(source: str, destination: str) -> dict:
    """
    Move a file from source to destination.

    args:
        str: source
        str: destination
    return:
        dict: result of the operation
    """
    # Validate both paths are within project directory
    if not validate_path(source):
        return {"success": False, "message": f"Source path {source} is outside the project directory.", "data": None}
    if not validate_path(destination):
        return {"success": False, "message": f"Destination path {destination} is outside the project directory.", "data": None}
    
    try:
        shutil.move(source, destination)
        return {"success": True, "message": "OK", "data": None}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

def rename_file(old_name: str, new_name: str) -> dict:
    """
    Rename a file from old_name to new_name.

    args:
        str: old_name
        str: new_name
    return:
        dict: result of the operation
    """
    # Validate both paths are within project directory
    if not validate_path(old_name):
        return {"success": False, "message": f"Old path {old_name} is outside the project directory.", "data": None}
    if not validate_path(new_name):
        return {"success": False, "message": f"New path {new_name} is outside the project directory.", "data": None}
    
    try:
        os.rename(old_name, new_name)
        return {"success": True, "message": "OK", "data": None}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

def append_to_file(filepath: str, content: str) -> dict:
    """
    Append content to the end of a file.

    args:
        str: filepath
        str: content
    return:
        dict: result of the operation
    """
    # Validate path is within project directory
    if not validate_path(filepath):
        return {"success": False, "message": f"Path {filepath} is outside the project directory.", "data": None}
    
    try:
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "message": "OK", "data": None}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
