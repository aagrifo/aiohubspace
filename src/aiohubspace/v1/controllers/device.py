"""Controller that holds top-level devices"""

from ..device import HubspaceDevice, get_hs_device
from ..models import device
from ..models.resource import DeviceInformation, ResourceTypes
from .base import BaseResourcesController


class DeviceController(BaseResourcesController[device.Device]):
    """Controller that identifies top-level components."""

    ITEM_TYPE_ID = ResourceTypes.DEVICE
    ITEM_TYPES = []
    ITEM_CLS = device.Device

    async def initialize_elem(self, hs_device: HubspaceDevice) -> None:
        """Initialize the element"""
        self._logger.info("Initializing %s", hs_device.id)
        available: bool = False
        for state in hs_device.states:
            if state.functionClass == "available":
                available = state.value

        self._items[hs_device.id] = device.Device(
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
        )

    def get_filtered_devices(self, initial_data: list[dict]) -> list[dict]:
        """Find parent devices"""
        parents: dict = {}
        for element in initial_data:
            if element["typeId"] != self.ITEM_TYPE_ID.value:
                self._logger.debug(
                    "TypeID [%s] does not match %s",
                    element["typeId"],
                    self.ITEM_TYPE_ID.value,
                )
                continue
            device: HubspaceDevice = get_hs_device(element)
            if device.device_id not in parents or device.children:
                parents[device.device_id] = device
        return list(parents.values())
