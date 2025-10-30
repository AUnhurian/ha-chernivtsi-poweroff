"""Constants for the Chernivtsi Power Offline integration."""

from enum import StrEnum

DOMAIN = "chernivtsi_poweroff"

POWEROFF_GROUP_CONF = "poweroff_group"

UPDATE_INTERVAL = 600

STATE_ON = "Power ON"
STATE_OFF = "Power OFF"
STATE_POSSIBLE_ON = "Power POSSIBLE ON"


class PowerOffGroup(StrEnum):
    """PowerOff groups in Chernivtsi oblast."""

    One = "1"
    Two = "2"
    Three = "3"
    Four = "4"
    Five = "5"
    Six = "6"
    Seven = "7"
    Eight = "8"
    Nine = "9"
    Ten = "10"
    Eleven = "11"
    Twelve = "12"
