import pytest

from aiohubspace.v1.controllers.device import DeviceController
from aiohubspace.v1.models.resource import DeviceInformation
from aiohubspace.v1.models.sensor import HubspaceSensor

from .. import utils

a21_light = utils.create_devices_from_data("light-a21.json")[0]
zandra_light = utils.create_devices_from_data("fan-ZandraFan.json")[1]
freezer = utils.create_devices_from_data("freezer.json")[0]


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
    assert dev.sensors == {
        "wifi-rssi": HubspaceSensor(
            id="wifi-rssi",
            owner="30a2df8c-109b-42c2-aed6-a6b30c565f8f",
            value=-50,
            instance=None,
            unit="dB",
        )
    }
    assert dev.binary_sensors == {}


@pytest.mark.asyncio
async def test_initialize_binary_sensors(mocked_controller):
    await mocked_controller.initialize_elem(freezer)
    assert len(mocked_controller.items) == 1
    dev = mocked_controller.items[0]
    assert dev.id == freezer.id
    assert dev.available is True
    assert dev.device_information == DeviceInformation(
        device_class=freezer.device_class,
        default_image=freezer.default_image,
        default_name=freezer.default_name,
        manufacturer=freezer.manufacturerName,
        model=freezer.model,
        name=freezer.friendly_name,
        parent_id=freezer.device_id,
    )
    assert dev.sensors == {
        "wifi-rssi": HubspaceSensor(
            id="wifi-rssi",
            owner="596c120d-4e0d-4e33-ae9a-6330dcf2cbb5",
            value=-71,
            instance=None,
            unit="dB",
        )
    }
    assert dev.binary_sensors == {
        "error|freezer-high-temperature-alert": HubspaceSensor(
            id="error|freezer-high-temperature-alert",
            owner="596c120d-4e0d-4e33-ae9a-6330dcf2cbb5",
            value="normal",
            instance="freezer-high-temperature-alert",
        ),
        "error|fridge-high-temperature-alert": HubspaceSensor(
            id="error|fridge-high-temperature-alert",
            owner="596c120d-4e0d-4e33-ae9a-6330dcf2cbb5",
            value="alerting",
            instance="fridge-high-temperature-alert",
        ),
        "error|mcu-communication-failure": HubspaceSensor(
            id="error|mcu-communication-failure",
            owner="596c120d-4e0d-4e33-ae9a-6330dcf2cbb5",
            value="normal",
            instance="mcu-communication-failure",
        ),
        "error|temperature-sensor-failure": HubspaceSensor(
            id="error|temperature-sensor-failure",
            owner="596c120d-4e0d-4e33-ae9a-6330dcf2cbb5",
            value="normal",
            instance="temperature-sensor-failure",
        ),
    }


@pytest.mark.xfail(reason="Expecting raw HS data and given devices")
@pytest.mark.parametrize("file, expected_keys", [("light-a21.json", [a21_light.id])])
def test_get_filtered_devices(file, expected_keys, mocked_controller):
    data = utils.get_device_dump("light-a21.json")
    res = mocked_controller.get_filtered_devices(data)
    assert len(res) == len(expected_keys)
    for key in expected_keys:
        assert key in res
