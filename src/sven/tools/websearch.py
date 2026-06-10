import subprocess

def websearch(query: str) -> str:
    """Search web via duckduckgo"""
    """
    Args:
        query: Searchquery

    Returns:
        Searchresults
    """
    result = subprocess.run(["ddgr", "--noprompt", query], capture_output=True, text=True)
    return result
