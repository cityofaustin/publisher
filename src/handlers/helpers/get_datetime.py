from datetime import datetime
from pytz import timezone

# Returns the datetime in central time
def get_datetime():
    return datetime.now(timezone('US/Central')).isoformat()
