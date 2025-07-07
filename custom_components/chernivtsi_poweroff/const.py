"""Constants for the Chernivtsi Power Offline integration."""

from enum import StrEnum

DOMAIN = "chernivtsi_poweroff"

POWEROFF_GROUP_CONF = "poweroff_group"

UPDATE_INTERVAL = 600

STATE_ON = "Power ON"
STATE_OFF = "Power OFF"


class PowerOffGroup(StrEnum):
    """PowerOff groups in Chernivtsi oblast."""

    One = "1"
    Two = "2"
    Three = "3"
