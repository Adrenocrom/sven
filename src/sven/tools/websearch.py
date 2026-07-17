import subprocess

def websearch(query: str) -> dict:
    """
    Search the web via DuckDuckGo.

    Parameters
    ----------
    query : str
        The search string to submit to DuckDuckGo.  This can be a simple keyword,
        a phrase, or a more elaborate Boolean expression (e.g., "site:example.com
        \"error code\"").

    Returns
    -------
    list[str]
        A list of URLs that DuckDuckGo returns for the supplied query.

    Notes
    -----
    The results are intentionally minimal – only the raw URLs are returned.  
    If you want to investigate any of the links further, use the `webfetch`
    helper (or your own HTTP client) on the *interesting* URLs to fetch and
    inspect their content.
    """
    try:
        result = subprocess.run(
            ["py", "-m", "ddgr", "--noprompt", query],
            capture_output=True,
            text=True
        )
        return {"success": True, "message": "OK", "data": result.stdout}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

