"""The Chernivtsi Power Offline integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import POWEROFF_GROUP_CONF, PowerOffGroup
from .coordinator import ChernivtsiPowerOffCoordinator

PLATFORMS: list[Platform] = [Platform.CALENDAR, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Chernivtsi Power Offline from a config entry."""
    coordinator = ChernivtsiPowerOffCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options are updated."""
    # Unload current platforms
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    # Update coordinator with new group if changed
    if entry.runtime_data and isinstance(entry.runtime_data, ChernivtsiPowerOffCoordinator):
        coordinator = entry.runtime_data
        new_group = PowerOffGroup(entry.data[POWEROFF_GROUP_CONF])
        if coordinator.group != new_group:
            coordinator.update_group(new_group)
    
    # Reload platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Trigger immediate refresh
    if entry.runtime_data and isinstance(entry.runtime_data, ChernivtsiPowerOffCoordinator):
        await entry.runtime_data.async_request_refresh()


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
