import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import STATE_OFF, STATE_ON, STATE_POSSIBLE_ON
from .coordinator import ChernivtsiPowerOffCoordinator

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class ChernivtsiPowerOffSensorDescription(SensorEntityDescription):
    """Chernivtsi PowerOff entity description."""

    val_func: Callable[[ChernivtsiPowerOffCoordinator], Any]


SENSOR_TYPES: tuple[ChernivtsiPowerOffSensorDescription, ...] = (
    ChernivtsiPowerOffSensorDescription(
        key="electricity",
        icon="mdi:transmission-tower",
        device_class=SensorDeviceClass.ENUM,
        name="Power state",
        options=[STATE_ON, STATE_OFF, STATE_POSSIBLE_ON],
        val_func=lambda coordinator: coordinator.current_state,
    ),
    ChernivtsiPowerOffSensorDescription(
        key="next_poweroff",
        icon="mdi:calendar-remove",
        device_class=SensorDeviceClass.TIMESTAMP,
        name="Next power off",
        val_func=lambda coordinator: coordinator.next_poweroff,
    ),
    ChernivtsiPowerOffSensorDescription(
        key="next_poweron",
        icon="mdi:calendar-check",
        device_class=SensorDeviceClass.TIMESTAMP,
        name="Next power on",
        val_func=lambda coordinator: coordinator.next_poweron,
    ),
    ChernivtsiPowerOffSensorDescription(
        key="last_update",
        icon="mdi:clock-outline",
        device_class=SensorDeviceClass.TIMESTAMP,
        name="Last update",
        val_func=lambda coordinator: coordinator.last_update_time,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Chernivtsi PowerOff sensors."""
    LOGGER.debug("Setup new entry: %s", config_entry)
    coordinator: ChernivtsiPowerOffCoordinator = config_entry.runtime_data
    async_add_entities(ChernivtsiPowerOffSensor(coordinator, description) for description in SENSOR_TYPES)


class ChernivtsiPowerOffSensor(SensorEntity):
    def __init__(
        self,
        coordinator: ChernivtsiPowerOffCoordinator,
        entity_description: ChernivtsiPowerOffSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}-" f"{coordinator.group}-" f"{self.entity_description.key}"
        )

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self.entity_description.val_func(self.coordinator)  # type: ignore
