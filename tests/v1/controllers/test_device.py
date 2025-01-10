import pytest

from aiohubspace.v1.controllers.device import DeviceController, split_sensor_data
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
        wifi_mac="b31d2f3f-86f6-4e7e-b91b-4fbc161d410d",
        ble_mac="9c70c759-1d54-4f61-a067-bb4294bef7ae",
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
        wifi_mac="351cccd0-87ff-41b3-b18c-568cf781d56d",
        ble_mac="c2e189e8-c80c-4948-9492-14ac390f480d",
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


def test_get_filtered_devices(mocked_controller):
    data = utils.get_raw_dump("raw_hs_data.json")
    res = mocked_controller.get_filtered_devices(data)
    expected_devs = [
        "b16fc78d-4639-41a7-8a10-868405c412d6",
        "99a03fb7-ebaa-4fc2-a7b5-df223003b127",
        "84338ebe-7ddf-4bfa-9753-3ee8cdcc8da6",
        "4a3eeb61-17e0-472b-bef5-576d78cb06df",
    ]
    actual_devs = [x.id for x in res]
    assert len(actual_devs) == len(expected_devs)
    for key in expected_devs:
        assert key in actual_devs


@pytest.mark.asyncio
async def test_update_elem_sensor(mocked_controller):
    await mocked_controller.initialize_elem(a21_light)
    assert len(mocked_controller.items) == 1
    dev = mocked_controller.items[0]
    assert dev.id == a21_light.id
    dev_update: utils.HubspaceDevice = utils.create_devices_from_data("light-a21.json")[
        0
    ]
    unavail = utils.HubspaceState(
        functionClass="available",
        value=False,
    )
    utils.modify_state(dev_update, unavail)
    rssi = utils.HubspaceState(
        functionClass="wifi-rssi",
        value=40,
    )
    utils.modify_state(dev_update, rssi)
    await mocked_controller.update_elem(dev_update)
    assert dev.available is False
    assert dev.sensors["wifi-rssi"].value == 40


@pytest.mark.asyncio
async def test_update_elem_binary_sensor(mocked_controller):
    await mocked_controller.initialize_elem(freezer)
    assert len(mocked_controller.items) == 1
    dev = mocked_controller.items[0]
    assert dev.id == freezer.id
    dev_update: utils.HubspaceDevice = utils.create_devices_from_data("freezer.json")[0]
    temp_sensor_failure = utils.HubspaceState(
        functionClass="error",
        functionInstance="temperature-sensor-failure",
        value="alerting",
    )
    utils.modify_state(dev_update, temp_sensor_failure)
    await mocked_controller.update_elem(dev_update)
    assert dev.binary_sensors["error|temperature-sensor-failure"].value == "alerting"


@pytest.mark.parametrize(
    "state, expected_val, expected_unit",
    [
        (
            utils.HubspaceState(functionClass="doesnt_matter", value="4000K"),
            "4000",
            "K",
        ),
        (
            utils.HubspaceState(functionClass="doesnt_matter", value="normal"),
            "normal",
            None,
        ),
        (utils.HubspaceState(functionClass="doesnt_matter", value=4000), 4000, None),
    ],
)
def test_split_sensor_data(state, expected_val, expected_unit):
    actual_val, actual_unit = split_sensor_data(state)
    assert actual_val == expected_val
    assert actual_unit == expected_unit
