from dataclasses import dataclass, field

from .resource import DeviceInformation


@dataclass
class Device:
    """Representation of a Hubspace parent item"""

    id: str  # ID used when interacting with HubSpace
    available: bool
    device_information: DeviceInformation = field(default_factory=DeviceInformation)
