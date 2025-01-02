from dataclasses import dataclass, field

from ..models import features
from .resource import DeviceInformation, ResourceTypes


@dataclass
class Fan:
    """Representation of a Hubspace Fan"""

    id: str  # ID used when interacting with Hubspace
    available: bool

    on: features.OnFeature
    speed: features.SpeedFeature
    direction: features.DirectionFeature
    preset: features.PresetFeature

    # Defined at initialization
    instances: dict = field(default_factory=lambda: dict(), repr=False, init=False)
    device_information: DeviceInformation = field(default_factory=DeviceInformation)

    type: ResourceTypes = ResourceTypes.FAN

    def __init__(self, functions: list, **kwargs):
        for key, value in kwargs.items():
            if key == "instances":
                continue
            setattr(self, key, value)
        instances = {}
        for function in functions:
            try:
                if function["functionInstance"]:
                    instances[function["functionClass"]] = function["functionInstance"]
            except KeyError:
                continue
        self.instances = instances

    def get_instance(self, elem):
        """Lookup the instance associated with the elem"""
        return self.instances.get(elem, None)

    @property
    def supports_direction(self):
        return self.direction is not None

    @property
    def supports_on(self):
        return self.on is not None

    @property
    def supports_presets(self):
        return self.preset is not None

    @property
    def supports_speed(self):
        return self.speed is not None

    @property
    def is_on(self) -> bool:
        """Return bool if fan is currently powered on."""
        if self.on is not None:
            return self.on.on
        return False

    @property
    def current_direction(self) -> bool:
        """Return if the direction is forward"""
        return self.direction.forward

    @property
    def current_speed(self) -> int:
        """Current speed of the fan, as a percentage"""
        return self.speed.speed

    @property
    def current_preset(self) -> str | None:
        """Current fan preset"""
        if self.preset.enabled:
            return self.preset.func_instance
        else:
            return None


@dataclass
class FanPut:
    """States that can be updated for a Fan"""

    on: features.OnFeature | None = None
    speed: features.SpeedFeature | None = None
    direction: features.DirectionFeature | None = None
    preset: features.PresetFeature | None = None
