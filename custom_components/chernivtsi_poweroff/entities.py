"""Module for power off period entities."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from .const import STATE_OFF

@dataclass
class PowerOffPeriod:
    """Class for power off period."""

    start: int  # minutes from day's start
    end: int    # minutes from day's start
    today: bool
    state: str = STATE_OFF

    def to_datetime_period(self, tz_info) -> tuple[datetime, datetime]:
        """Convert to datetime period."""
        now = datetime.now().replace(tzinfo=tz_info)
        if not self.today:
            now += timedelta(days=1)

        # Normalize start and end to be within 0-1439 minutes (0:00-23:59)
        start_minutes = self.start % 1440
        end_minutes = self.end % 1440
        
        start_hour, start_minute = divmod(start_minutes, 60)
        end_hour, end_minute = divmod(end_minutes, 60)
        
        start = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        end = now.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
        
        # If end is before start or end is exactly 24:00 (1440 minutes), it's next day
        if end < start or self.end >= 1440:
            end += timedelta(days=1)
        
        return start, end
