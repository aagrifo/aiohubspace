import pytest

from aiohubspace.v1.controllers.device import DeviceController
from aiohubspace.v1.models.resource import DeviceInformation

from .. import utils

a21_light = utils.create_devices_from_data("light-a21.json")[0]
zandra_light = utils.create_devices_from_data("fan-ZandraFan.json")[1]


@pytest.fixture
def mocked_controller(mocked_bridge, mocker):
    mocker.patch("time.time", return_value=12345)
    controller = DeviceController(mocked_bridge)
    yield controller


@pytest.mark.asyncio
async def test_initialize_a21(mocked_controller):
    await mocked_controller.initialize_elem(a21_light)
    assert len(mocked_controller.items) == 1
    dev = mocked_controller.items[0]
    assert dev.id == a21_light.id
    assert dev.available is True
    assert dev.device_information == DeviceInformation(
        device_class=a21_light.device_class,
        default_image=a21_light.default_image,
        default_name=a21_light.default_name,
        manufacturer=a21_light.manufacturerName,
        model=a21_light.model,
        name=a21_light.friendly_name,
        parent_id=a21_light.device_id,
    )


@pytest.mark.xfail(reason="Expecting raw HS data and given devices")
@pytest.mark.parametrize("file, expected_keys", [("light-a21.json", [a21_light.id])])
def test_get_filtered_devices(file, expected_keys, mocked_controller):
    data = utils.get_device_dump("light-a21.json")
    res = mocked_controller.get_filtered_devices(data)
    assert len(res) == len(expected_keys)
    for key in expected_keys:
        assert key in res
