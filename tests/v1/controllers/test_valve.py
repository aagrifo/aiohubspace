"""Test ValveController"""

import pytest

from aiohubspace.v1.controllers.valve import ValveController, features
from aiohubspace.v1.device import HubspaceState

from .. import utils

valve = utils.create_devices_from_data("water-timer.json")[0]


@pytest.fixture
def mocked_controller(mocked_bridge, mocker):
    mocker.patch("time.time", return_value=12345)
    controller = ValveController(mocked_bridge)
    yield controller


@pytest.mark.asyncio
async def test_initialize_multi(mocked_controller):
    await mocked_controller.initialize_elem(valve)
    assert len(mocked_controller.items) == 1
    dev = mocked_controller.items[0]
    assert dev.id == "60eb18c9-8510-4bcd-be3f-493dfb351268"
    assert dev.open == {
        None: features.OpenFeature(open=False, func_class="power", func_instance=None),
        "spigot-1": features.OpenFeature(
            open=False, func_class="toggle", func_instance="spigot-1"
        ),
        "spigot-2": features.OpenFeature(
            open=True, func_class="toggle", func_instance="spigot-2"
        ),
    }


@pytest.mark.asyncio
async def test_turn_on_multi(mocked_controller):
    await mocked_controller.initialize_elem(valve)
    dev = mocked_controller.items[0]
    await mocked_controller.turn_on(valve.id, instance="spigot-1")
    req = utils.get_json_call(mocked_controller)
    assert req["metadeviceId"] == valve.id
    expected_states = [
        {
            "functionClass": "toggle",
            "functionInstance": "spigot-1",
            "lastUpdateTime": 12345,
            "value": "on",
        }
    ]
    utils.ensure_states_sent(mocked_controller, expected_states)
    assert dev.open == {
        None: features.OpenFeature(open=False, func_class="power", func_instance=None),
        "spigot-1": features.OpenFeature(
            open=True, func_class="toggle", func_instance="spigot-1"
        ),
        "spigot-2": features.OpenFeature(
            open=True, func_class="toggle", func_instance="spigot-2"
        ),
    }


@pytest.mark.asyncio
async def test_turn_off(mocked_controller):
    await mocked_controller.initialize_elem(valve)
    dev = mocked_controller.items[0]
    await mocked_controller.turn_off(valve.id, instance="spigot-2")
    req = utils.get_json_call(mocked_controller)
    assert req["metadeviceId"] == valve.id
    expected_states = [
        {
            "functionClass": "toggle",
            "functionInstance": "spigot-2",
            "lastUpdateTime": 12345,
            "value": "off",
        }
    ]
    utils.ensure_states_sent(mocked_controller, expected_states)
    assert dev.open == {
        None: features.OpenFeature(open=False, func_class="power", func_instance=None),
        "spigot-1": features.OpenFeature(
            open=False, func_class="toggle", func_instance="spigot-1"
        ),
        "spigot-2": features.OpenFeature(
            open=False, func_class="toggle", func_instance="spigot-2"
        ),
    }


@pytest.mark.asyncio
async def test_update_elem(mocked_controller):
    await mocked_controller.initialize_elem(valve)
    assert len(mocked_controller.items) == 1
    dev_update = utils.create_devices_from_data("water-timer.json")[0]
    new_states = [
        HubspaceState(
            **{
                "functionClass": "toggle",
                "value": "on",
                "lastUpdateTime": 0,
                "functionInstance": "spigot-1",
            }
        ),
        HubspaceState(
            **{
                "functionClass": "toggle",
                "value": "off",
                "lastUpdateTime": 0,
                "functionInstance": "spigot-2",
            }
        ),
    ]
    for state in new_states:
        utils.modify_state(dev_update, state)
    await mocked_controller.update_elem(dev_update)
    dev = mocked_controller.items[0]
    assert dev.open["spigot-1"].open is True
    assert dev.open["spigot-2"].open is False
