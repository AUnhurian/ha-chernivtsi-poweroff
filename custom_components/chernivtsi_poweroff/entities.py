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

        start_hour, start_minute = divmod(self.start, 60)
        end_hour, end_minute = divmod(self.end, 60)
        start = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        end = now.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
        if end < start:
            end += timedelta(days=1)
        return start, end
