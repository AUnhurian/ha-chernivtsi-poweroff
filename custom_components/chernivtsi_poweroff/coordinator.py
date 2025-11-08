"""Provides the ChernivtsiPowerOffCoordinator class for polling power off periods."""

from datetime import datetime, timedelta
import logging

from homeassistant.components.calendar import CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    POWEROFF_GROUP_CONF,
    UPDATE_INTERVAL,
    PowerOffGroup,
    STATE_ON,
    STATE_OFF,
    STATE_POSSIBLE_ON,
)
from .energyua_scrapper import EnergyUaScrapper
from .entities import PowerOffPeriod

LOGGER = logging.getLogger(__name__)

TIMEFRAME_TO_CHECK = timedelta(hours=24)


class ChernivtsiPowerOffCoordinator(DataUpdateCoordinator):
    """Coordinates the polling of power off periods."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.hass = hass
        self.config_entry = config_entry
        self.group: PowerOffGroup = config_entry.data[POWEROFF_GROUP_CONF]
        self.api = EnergyUaScrapper(self.group)
        self.periods: list[PowerOffPeriod] = []
        self.last_update: datetime | None = None

    async def _async_update_data(self) -> dict:
        """Fetch power off periods from scrapper."""
        LOGGER.debug("Starting data update for group %s", self.group)
        try:
            await self._fetch_periods()
            self.last_update = dt_util.now()
            LOGGER.debug(
                "Successfully updated data for group %s. Found %d periods. Last update: %s",
                self.group,
                len(self.periods),
                self.last_update,
            )
            return {}  # noqa: TRY300
        except Exception as err:
            LOGGER.exception("Cannot obtain power offs periods for group %s", self.group)
            msg = f"Power offs not polled: {err}"
            raise UpdateFailed(msg) from err

    async def _fetch_periods(self) -> None:
        self.periods = await self.api.get_power_off_periods()

    def _get_next_power_change_dt(self, on: bool) -> datetime | None:
        """Get the next power on/off."""
        now = dt_util.now()
        events = self.get_events_between(
            now,
            now + TIMEFRAME_TO_CHECK,
        )
        if on:
            dts = sorted(event.end for event in events)
        else:
            dts = sorted(event.start for event in events)
        LOGGER.debug("Next dts: %s", dts)
        for dt in dts:
            if dt > now:
                return dt  # type: ignore
        return None

    @property
    def next_poweroff(self) -> datetime | None:
        """Get the next poweroff time."""
        dt = self._get_next_power_change_dt(on=False)
        LOGGER.debug("Next poweroff: %s", dt)
        return dt

    @property
    def next_poweron(self) -> datetime | None:
        """Get next connectivity time."""
        dt = self._get_next_power_change_dt(on=True)
        LOGGER.debug("Next powerof: %s", dt)
        return dt

    @property
    def current_state(self) -> str:
        """Get the current state."""
        now = dt_util.now()
        # OFF event has priority
        off_event = self.get_event_at(now)
        if off_event:
            return STATE_OFF
        # If any POSSIBLE_ON period matches now, reflect that
        for period in self.periods:
            if period.state != STATE_POSSIBLE_ON:
                continue
            start, end = period.to_datetime_period(now.tzinfo)
            if start <= now <= end:
                return STATE_POSSIBLE_ON
        return STATE_ON

    def get_event_at(self, at: datetime) -> CalendarEvent | None:
        """Get the current event."""
        # Check OFF periods first (higher priority)
        for period in self.periods:
            if period.state == STATE_OFF:
                start, end = period.to_datetime_period(at.tzinfo)
                if start <= at <= end:
                    return self._get_calendar_event(start, end, STATE_OFF)
        # Check POSSIBLE_ON periods
        for period in self.periods:
            if period.state == STATE_POSSIBLE_ON:
                start, end = period.to_datetime_period(at.tzinfo)
                if start <= at <= end:
                    return self._get_calendar_event(start, end, STATE_POSSIBLE_ON)
        return None

    def get_events_between(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Get all events (both OFF and POSSIBLE_ON periods)."""
        events = []
        for period in self.periods:
            if period.state not in (STATE_OFF, STATE_POSSIBLE_ON):
                continue
            start, end = period.to_datetime_period(start_date.tzinfo)
            if start_date <= start <= end_date or start_date <= end <= end_date:
                events.append(self._get_calendar_event(start, end, period.state))
        return events

    def _get_calendar_event(self, start: datetime, end: datetime, state: str) -> CalendarEvent:
        """Create a calendar event with appropriate summary based on state."""
        return CalendarEvent(
            start=start,
            end=end,
            summary=state,
        )

    @property
    def last_update_time(self) -> datetime | None:
        """Get the last successful update timestamp."""
        return self.last_update

    def update_group(self, new_group: PowerOffGroup) -> None:
        """Update the group and recreate the scraper."""
        self.group = new_group
        self.api = EnergyUaScrapper(new_group)
        self.periods = []
        self.last_update = None
