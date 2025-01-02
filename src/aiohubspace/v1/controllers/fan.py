"""Controller holding and managing Hubspace resources of type `fan`."""

from .. import device
from ..device import HubspaceDevice
from ..models import fan, features
from ..models.resource import DeviceInformation, ResourceTypes
from ..util import ordered_list_item_to_percentage
from .base import BaseResourcesController


class FanController(BaseResourcesController[fan.Fan]):
    """Controller holding and managing Hubspace resources of type `fan`."""

    ITEM_TYPE_ID = ResourceTypes.DEVICE
    ITEM_TYPES = [ResourceTypes.FAN]
    ITEM_CLS = fan.Fan
    ITEM_MAPPING = {
        "on": "power",
        "speed": "fan-speed",
        "direction": "fan-reverse",
    }

    async def turn_on(self, device_id: str) -> None:
        """Turn on the fan."""
        await self.set_state(device_id, on=True)

    async def turn_off(self, device_id: str) -> None:
        """Turn off the fan."""
        await self.set_state(device_id, on=False)

    async def set_speed(self, device_id: str, speed: int) -> None:
        """Set the speed of the fan, as a percentage."""
        await self.set_state(device_id, on=True, speed=speed)

    async def set_direction(self, device_id: str, forward: bool) -> None:
        """Set the direction of the fan to forward."""
        cur_item = self.get_device(device_id)
        if not cur_item.is_on:
            # Thanks Hubspace for this one! Additionally, turning it on and setting
            # direction at the same time does not work as expected
            self._logger.info("Fan is not running so direction will not be set")
        await self.set_state(device_id, forward=forward)

    async def set_preset(self, device_id: str, preset: bool) -> None:
        """Set the preset of the fan."""
        await self.set_state(device_id, on=True, preset=preset)

    async def initialize_elem(self, hs_device: HubspaceDevice) -> None:
        """Initialize the element"""
        self._logger.info("Initializing %s", hs_device.id)
        available: bool = False
        on: features.OnFeature | None = None
        speed: features.SpeedFeature | None = None
        direction: features.DirectionFeature | None = None
        preset: features.PresetFeature | None = None
        for state in hs_device.states:
            if state.functionClass == "power":
                on = features.OnFeature(on=state.value == "on")
            elif state.functionClass == "fan-speed":
                speeds = device.get_function_from_device(
                    hs_device, state.functionClass, state.functionInstance
                )
                tmp_speed = set()
                for value in speeds["values"]:
                    if not value["name"].endswith("-000"):
                        tmp_speed.add(value["name"])
                speeds = list(sorted(tmp_speed))
                percentage = ordered_list_item_to_percentage(speeds, state.value)
                speed = features.SpeedFeature(speed=percentage, speeds=speeds)
            elif state.functionClass == "fan-reverse":
                direction = features.DirectionFeature(forward=state.value == "forward")
            elif state.functionClass == "toggle":
                # I have only seen fans with a single preset
                preset = features.PresetFeature(
                    enabled=state.value == "on",
                    func_class=state.functionClass,
                    func_instance=state.functionInstance,
                )
            elif state.functionClass == "available":
                available = state.value

        self._items[hs_device.id] = fan.Fan(
            hs_device.functions,
            id=hs_device.id,
            available=available,
            device_information=DeviceInformation(
                device_class=hs_device.device_class,
                default_image=hs_device.default_image,
                default_name=hs_device.default_name,
                manufacturer=hs_device.manufacturerName,
                model=hs_device.model,
                name=hs_device.friendly_name,
                parent_id=hs_device.device_id,
            ),
            on=on,
            speed=speed,
            direction=direction,
            preset=preset,
        )

    async def update_elem(self, hs_device: HubspaceDevice) -> None:
        cur_item = self.get_device(hs_device.id)
        for state in hs_device.states:
            if state.functionClass == "power":
                cur_item.on.on = state.value == "on"
            elif state.functionClass == "fan-speed":
                cur_item.speed.speed = ordered_list_item_to_percentage(
                    cur_item.speed.speeds, state.value
                )
            elif state.functionClass == "fan-reverse":
                cur_item.direction.forward = state.value == "forward"
            elif state.functionClass == "toggle":
                cur_item.preset.enabled = state.value == "on"
            elif state.functionClass == "available":
                cur_item.available = state.value

    async def set_state(
        self,
        device_id: str,
        on: bool | None = None,
        speed: int | None = None,
        forward: bool | None = None,
        preset: bool | None = None,
    ) -> None:
        """Set supported feature(s) to fan resource."""
        update_obj = fan.FanPut()
        cur_item = self.get_device(device_id)
        if on is not None:
            update_obj.on = features.OnFeature(on=on)
        if speed is not None:
            if speed == 0:
                update_obj.on = features.OnFeature(on=False)
            else:
                update_obj.speed = features.SpeedFeature(
                    speed=speed, speeds=cur_item.speed.speeds
                )
        if preset is not None:
            update_obj.preset = features.PresetFeature(
                enabled=preset,
                func_class=cur_item.preset.func_class,
                func_instance=cur_item.preset.func_instance,
            )
        if forward is not None:
            update_obj.direction = features.DirectionFeature(forward=forward)
        await self.update(device_id, update_obj)
