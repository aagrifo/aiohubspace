"""Controller that holds top-level devices"""

from ..device import HubspaceDevice, get_hs_device
from ..models import device, sensor
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
        sensors: dict[str, sensor.HubspaceSensor] = {}
        binary_sensors: dict[str, sensor.HubspaceSensor] = {}
        for state in hs_device.states:
            if state.functionClass == "available":
                available = state.value
            elif state.functionClass in sensor.MAPPED_SENSORS:
                sensors[state.functionClass] = sensor.HubspaceSensor(
                    id=state.functionClass,
                    owner=hs_device.device_id,
                    value=state.value,
                )
            elif state.functionClass in sensor.BINARY_SENSORS:
                key = f"{state.functionClass}|{state.functionInstance}"
                binary_sensors[key] = sensor.HubspaceSensor(
                    id=key,
                    owner=hs_device.device_id,
                    value=state.value,
                    instance=state.functionInstance,
                )

        self._items[hs_device.id] = device.Device(
            id=hs_device.id,
            available=available,
            sensors=sensors,
            binary_sensors=binary_sensors,
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

    async def update_elem(self, hs_device: HubspaceDevice) -> None:
        cur_item = self.get_device(hs_device.id)
        for state in hs_device.states:
            if state.functionClass == "available":
                cur_item.available = state.value
            elif state.functionClass in sensor.MAPPED_SENSORS:
                cur_item.sensors[state.functionClass].value = state.value
