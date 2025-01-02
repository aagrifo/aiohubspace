"""Controller holding and managing Hubspace resources of type `lock`."""

from ..device import HubspaceDevice
from ..models import features, lock
from ..models.resource import DeviceInformation, ResourceTypes
from .base import BaseResourcesController


class LockController(BaseResourcesController[lock.Lock]):
    """Controller holding and managing Hubspace resources of type `lock`."""

    ITEM_TYPE_ID = ResourceTypes.DEVICE
    ITEM_TYPES = [ResourceTypes.LOCK]
    ITEM_CLS = lock.Lock
    ITEM_MAPPING = {"position": "lock-control"}

    async def lock(self, device_id: str) -> None:
        """Engage the lock"""
        await self.set_state(
            device_id, lock_position=features.CurrentPositionEnum.LOCKING
        )

    async def unlock(self, device_id: str) -> None:
        """Disengage the lock"""
        await self.set_state(
            device_id, lock_position=features.CurrentPositionEnum.UNLOCKING
        )

    async def initialize_elem(self, hs_device: HubspaceDevice) -> None:
        """Initialize the element"""
        self._logger.info("Initializing %s", hs_device.id)
        available: bool = False
        current_position: features.CurrentPositionFeature | None = None
        for state in hs_device.states:
            if state.functionClass == "lock-control":
                current_position = features.CurrentPositionFeature(
                    position=features.CurrentPositionEnum(state.value)
                )
            elif state.functionClass == "available":
                available = state.value

        self._items[hs_device.id] = lock.Lock(
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
            position=current_position,
        )

    async def update_elem(self, hs_device: HubspaceDevice) -> None:
        cur_item = self.get_device(hs_device.id)
        for state in hs_device.states:
            if state.functionClass == "lock-control":
                cur_item.position.position = features.CurrentPositionEnum(state.value)
            elif state.functionClass == "available":
                cur_item.available = state.value

    async def set_state(
        self,
        device_id: str,
        lock_position: features.CurrentPositionEnum | None = None,
    ) -> None:
        """Set supported feature(s) to fan resource."""
        update_obj = lock.LockPut()
        if lock_position is not None:
            update_obj.position = features.CurrentPositionFeature(
                position=lock_position
            )
        await self.update(device_id, update_obj)
