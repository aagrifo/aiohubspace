from dataclasses import dataclass

MAPPED_SENSORS = [
    "battery-level",
    "output-voltage-switch",
    "watts",
    "wifi-rssi",
]


@dataclass
class HubSpaceSensor:
    id: str
    owner: str
    value: str | int | float | None
