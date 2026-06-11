import datetime

def getdatetime() -> dict:
    """gets current datetime"""
    try:
        now = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
        return {"success": True, "message": "OK", "data": now}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

