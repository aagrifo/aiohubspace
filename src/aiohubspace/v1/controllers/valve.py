"""Controller holding and managing Hubspace resources of type `valve`."""

from ..device import HubspaceDevice
from ..models import features, valve
from ..models.resource import DeviceInformation, ResourceTypes
from .base import BaseResourcesController


class ValveController(BaseResourcesController[valve.Valve]):
    """Controller holding and managing Hubspace resources of type `valve`.

    A valve can have one or more toggleable elements. They are controlled
    by their functionInstance.
    """

    ITEM_TYPE_ID = ResourceTypes.DEVICE
    ITEM_TYPES = [ResourceTypes.WATER_TIMER]
    ITEM_CLS = valve.Valve
    ITEM_MAPPING = {}

    async def turn_on(self, device_id: str, instance: str | None = None) -> None:
        """Open the valve"""
        await self.set_state(device_id, valve_open=True, instance=instance)

    async def turn_off(self, device_id: str, instance: str | None = None) -> None:
        """Close the valve"""
        await self.set_state(device_id, valve_open=False, instance=instance)

    async def initialize_elem(self, hs_device: HubspaceDevice) -> None:
        """Initialize the element"""
        self._logger.info("Initializing %s", hs_device.id)
        available: bool = False
        valve_open: dict[str, features.OpenFeature] = {}
        for state in hs_device.states:
            if state.functionClass in ["power", "toggle"]:
                valve_open[state.functionInstance] = features.OpenFeature(
                    open=state.value == "on",
                    func_class=state.functionClass,
                    func_instance=state.functionInstance,
                )
            elif state.functionClass == "available":
                available = state.value

        self._items[hs_device.id] = valve.Valve(
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
            open=valve_open,
        )

    async def update_elem(self, hs_device: HubspaceDevice) -> None:
        cur_item = self.get_device(hs_device.id)
        for state in hs_device.states:
            if state.functionClass in ["power", "toggle"]:
                cur_item.open[state.functionInstance].open = state.value == "on"
            elif state.functionClass == "available":
                cur_item.available = state.value

    async def set_state(
        self,
        device_id: str,
        valve_open: bool | None = None,
        instance: str | None = None,
    ) -> None:
        """Set supported feature(s) to fan resource."""
        update_obj = valve.ValvePut()
        if valve_open is not None:
            dev = self.get_device(device_id)
            try:
                update_obj.open = features.OpenFeature(
                    open=valve_open,
                    func_class=dev.open[instance].func_class,
                    func_instance=instance,
                )
            except KeyError:
                self._logger.info("Unable to find instance %s", instance)
        await self.update(device_id, update_obj)
