"""Controller holding and managing Hubspace resources of type `switch`."""

from ..device import HubspaceDevice
from ..models import features, switch
from ..models.resource import DeviceInformation, ResourceTypes
from .base import BaseResourcesController


class SwitchController(BaseResourcesController[switch.Switch]):
    """Controller holding and managing Hubspace resources of type `switch`.

    A switch can have one or more toggleable elements. They are controlled
    by their functionInstance.
    """

    ITEM_TYPE_ID = ResourceTypes.DEVICE
    ITEM_TYPES = [
        ResourceTypes.SWITCH,
        ResourceTypes.POWER_OUTLET,
        ResourceTypes.LANDSCAPE_TRANSFORMER,
    ]
    ITEM_CLS = switch.Switch
    ITEM_MAPPING = {}

    async def turn_on(self, device_id: str, instance: str | None = None) -> None:
        """Turn on the switch."""
        await self.set_state(device_id, on=True, instance=instance)

    async def turn_off(self, device_id: str, instance: str | None = None) -> None:
        """Turn off the switch."""
        await self.set_state(device_id, on=False, instance=instance)

    async def initialize_elem(self, hs_device: HubspaceDevice) -> None:
        """Initialize the element"""
        self._logger.info("Initializing %s", hs_device.id)
        available: bool = False
        on: dict[str, features.OnFeature] = {}
        for state in hs_device.states:
            if state.functionClass in ["power", "toggle"]:
                on[state.functionInstance] = features.OnFeature(
                    on=state.value == "on",
                    func_class=state.functionClass,
                    func_instance=state.functionInstance,
                )
            elif state.functionClass == "available":
                available = state.value

        self._items[hs_device.id] = switch.Switch(
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
        )

    async def update_elem(self, hs_device: HubspaceDevice) -> None:
        cur_item = self.get_device(hs_device.id)
        for state in hs_device.states:
            if state.functionClass in ["power", "toggle"]:
                cur_item.on[state.functionInstance].on = state.value == "on"
            elif state.functionClass == "available":
                cur_item.available = state.value

    async def set_state(
        self,
        device_id: str,
        on: bool | None = None,
        instance: str | None = None,
    ) -> None:
        """Set supported feature(s) to fan resource."""
        update_obj = switch.SwitchPut()
        if on is not None:
            dev = self.get_device(device_id)
            try:
                update_obj.on = features.OnFeature(
                    on=on,
                    func_class=dev.on[instance].func_class,
                    func_instance=instance,
                )
            except KeyError:
                self._logger.info("Unable to find instance %s", instance)
        await self.update(device_id, update_obj)
