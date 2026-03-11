from langchain_core.tools import tool
from datetime import datetime
import pytz

@tool
def get_current_datetime(timezone: str = "UTC") -> str:
    """
    Get the current date and time.
    
    Args:
        timezone: The timezone to get the time for (default: UTC). Examples: 'America/New_York', 'Europe/London'.
        
    Returns:
        A formatted string with the current date, time, and day of the week.
    """
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return now.strftime("%A, %B %d, %Y at %I:%M %p %Z")
    except Exception as e:
        return f"Error getting time for timezone {timezone}: {str(e)}"
