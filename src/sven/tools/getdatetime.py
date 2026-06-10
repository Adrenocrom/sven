import datetime

def getdatetime() -> str:
    """gets current datetime"""
    """
    Returns:
        Current Datetime
    """
    return datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y");
