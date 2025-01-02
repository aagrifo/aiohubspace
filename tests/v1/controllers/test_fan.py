"""Test FanController"""

import logging

import pytest

from aiohubspace.v1.controllers.fan import FanController, features
from aiohubspace.v1.device import HubspaceState

from .. import utils

zandra_fan = utils.create_devices_from_data("fan-ZandraFan.json")[0]


@pytest.fixture
def mocked_controller(mocked_bridge, mocker):
    mocker.patch("time.time", return_value=12345)
    controller = FanController(mocked_bridge)
    yield controller


@pytest.mark.asyncio
async def test_initialize_zandra(mocked_controller):
    await mocked_controller.initialize_elem(zandra_fan)
    assert len(mocked_controller.items) == 1
    dev = mocked_controller.items[0]
    assert dev.id == "066c0e38-c49b-4f60-b805-486dc07cab74"
    assert dev.on == features.OnFeature(on=True)
    assert dev.speed == features.SpeedFeature(
        speed=50,
        speeds=[
            "fan-speed-6-016",
            "fan-speed-6-033",
            "fan-speed-6-050",
            "fan-speed-6-066",
            "fan-speed-6-083",
            "fan-speed-6-100",
        ],
    )
    assert dev.direction == features.DirectionFeature(forward=False)


@pytest.mark.asyncio
async def test_turn_on(mocked_controller):
    await mocked_controller.initialize_elem(zandra_fan)
    assert len(mocked_controller.items) == 1
    dev = mocked_controller.items[0]
    dev.on.on = False
    await mocked_controller.turn_on(zandra_fan.id)
    req = utils.get_json_call(mocked_controller)
    assert req["metadeviceId"] == zandra_fan.id
    expected_states = [
        {
            "functionClass": "power",
            "functionInstance": "fan-power",
            "lastUpdateTime": 12345,
            "value": "on",
        }
    ]
    utils.ensure_states_sent(mocked_controller, expected_states)


@pytest.mark.asyncio
async def test_turn_off(mocked_controller):
    await mocked_controller.initialize_elem(zandra_fan)
    assert len(mocked_controller.items) == 1
    assert len(mocked_controller.items) == 1
    dev = mocked_controller.items[0]
    dev.on.on = True
    await mocked_controller.turn_off(zandra_fan.id)
    req = utils.get_json_call(mocked_controller)
    assert req["metadeviceId"] == zandra_fan.id
    expected_states = [
        {
            "functionClass": "power",
            "functionInstance": "fan-power",
            "lastUpdateTime": 12345,
            "value": "off",
        }
    ]
    utils.ensure_states_sent(mocked_controller, expected_states)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "speed, expected_speed",
    [
        # Speed of 0 should turn off
        (0, None),
        # Find the next highest value
        (1, "fan-speed-6-016"),
        # Exact value
        (16, "fan-speed-6-016"),
    ],
)
async def test_set_speed(speed, expected_speed, mocked_controller):
    await mocked_controller.initialize_elem(zandra_fan)
    assert len(mocked_controller.items) == 1
    dev = mocked_controller.items[0]
    if expected_speed:
        dev.on.on = False
    else:
        dev.on.on = True
    dev.speed.speed = "fan-speed-6-100"
    await mocked_controller.set_speed(zandra_fan.id, speed)
    req = utils.get_json_call(mocked_controller)
    assert req["metadeviceId"] == zandra_fan.id
    expected_states = [
        {
            "functionClass": "power",
            "functionInstance": "fan-power",
            "lastUpdateTime": 12345,
            "value": "on",
        },
    ]
    if expected_speed is None:
        expected_states[0]["value"] = "off"
    else:
        expected_states.append(
            {
                "functionClass": "fan-speed",
                "functionInstance": "fan-speed",
                "lastUpdateTime": 12345,
                "value": expected_speed,
            }
        )
    utils.ensure_states_sent(mocked_controller, expected_states)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "on",
    [
        (True,),
        (False,),
    ],
)
@pytest.mark.parametrize(
    "forward, value",
    [
        (True, "forward"),
        (False, "reverse"),
    ],
)
async def test_set_direction(on, forward, value, mocked_controller, caplog):
    caplog.set_level(logging.DEBUG)
    await mocked_controller.initialize_elem(zandra_fan)
    assert len(mocked_controller.items) == 1
    dev = mocked_controller.items[0]
    dev.on.on = False
    dev.direction.forward = not forward
    await mocked_controller.set_direction(zandra_fan.id, forward)
    req = utils.get_json_call(mocked_controller)
    assert req["metadeviceId"] == zandra_fan.id
    expected_states = [
        {
            "functionClass": "fan-reverse",
            "functionInstance": "fan-reverse",
            "lastUpdateTime": 12345,
            "value": value,
        },
    ]
    if not on:
        assert "Fan is not running so direction will not be set" in caplog.text
    utils.ensure_states_sent(mocked_controller, expected_states)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "on",
    [
        (True,),
        (False,),
    ],
)
@pytest.mark.parametrize(
    "preset, value",
    [
        (True, "enabled"),
        (False, "disabled"),
    ],
)
async def test_set_preset(on, preset, value, mocked_controller):
    await mocked_controller.initialize_elem(zandra_fan)
    assert len(mocked_controller.items) == 1
    dev = mocked_controller.items[0]
    dev.on.on = True
    dev.preset.enabled = not preset
    await mocked_controller.set_preset(zandra_fan.id, preset)
    req = utils.get_json_call(mocked_controller)
    assert req["metadeviceId"] == zandra_fan.id
    expected_states = [
        {
            "functionClass": "toggle",
            "functionInstance": "comfort-breeze",
            "lastUpdateTime": 12345,
            "value": value,
        },
    ]
    utils.ensure_states_sent(mocked_controller, expected_states)


@pytest.mark.asyncio
async def test_update_elem(mocked_controller):
    await mocked_controller.initialize_elem(zandra_fan)
    assert len(mocked_controller.items) == 1
    dev_update = utils.create_devices_from_data("fan-ZandraFan.json")[0]
    new_states = [
        HubspaceState(
            **{
                "functionClass": "toggle",
                "value": "disabled",
                "lastUpdateTime": 0,
                "functionInstance": "comfort-breeze",
            }
        ),
        HubspaceState(
            **{
                "functionClass": "fan-speed",
                "value": "fan-speed-6-016",
                "lastUpdateTime": 0,
                "functionInstance": "fan-speed",
            }
        ),
        HubspaceState(
            **{
                "functionClass": "fan-reverse",
                "value": "forward",
                "lastUpdateTime": 0,
                "functionInstance": "fan-reverse",
            }
        ),
        HubspaceState(
            **{
                "functionClass": "power",
                "value": "off",
                "lastUpdateTime": 0,
                "functionInstance": "fan-power",
            }
        ),
    ]
    for state in new_states:
        utils.modify_state(dev_update, state)
    await mocked_controller.update_elem(dev_update)
    dev = mocked_controller.items[0]
    assert dev.preset.enabled is False
    assert dev.speed.speed == 16
    assert dev.direction.forward is True
    assert dev.on.on is False
