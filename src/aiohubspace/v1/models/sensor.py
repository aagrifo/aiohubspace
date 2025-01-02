from dataclasses import dataclass, field

MAPPED_SENSORS = [
    "battery-level",
    "output-voltage-switch",
    "watts",
    "wifi-rssi",
]

BINARY_SENSORS = ["error"]


@dataclass
class HubspaceSensor:
    id: str
    owner: str
    value: str | int | float | None

    instance: str | None = field(default=None)
