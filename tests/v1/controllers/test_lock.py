"""Test LockController"""

import pytest

from aiohubspace.v1.controllers.lock import LockController, features
from aiohubspace.v1.device import HubspaceState

from .. import utils

lock = utils.create_devices_from_data("door-lock-TBD.json")[0]


@pytest.fixture
def mocked_controller(mocked_bridge, mocker):
    mocker.patch("time.time", return_value=12345)
    controller = LockController(mocked_bridge)
    yield controller


@pytest.mark.asyncio
async def test_initialize(mocked_controller):
    await mocked_controller.initialize_elem(lock)
    assert len(mocked_controller.items) == 1
    dev = mocked_controller.items[0]
    assert dev.id == "698e8a63-e8cb-4335-ba6b-83ca69d378f2"
    assert dev.position == features.CurrentPositionFeature(
        position=features.CurrentPositionEnum.LOCKED
    )


@pytest.mark.asyncio
async def test_lock(mocked_controller):
    await mocked_controller.initialize_elem(lock)
    assert len(mocked_controller.items) == 1
    await mocked_controller.lock(lock.id)
    req = utils.get_json_call(mocked_controller)
    assert req["metadeviceId"] == lock.id
    expected_states = [
        {
            "functionClass": "lock-control",
            "functionInstance": None,
            "lastUpdateTime": 12345,
            "value": features.CurrentPositionEnum.LOCKING.value,
        }
    ]
    utils.ensure_states_sent(mocked_controller, expected_states)


@pytest.mark.asyncio
async def test_unlock(mocked_controller):
    await mocked_controller.initialize_elem(lock)
    assert len(mocked_controller.items) == 1
    await mocked_controller.unlock(lock.id)
    req = utils.get_json_call(mocked_controller)
    assert req["metadeviceId"] == lock.id
    expected_states = [
        {
            "functionClass": "lock-control",
            "functionInstance": None,
            "lastUpdateTime": 12345,
            "value": features.CurrentPositionEnum.UNLOCKING.value,
        }
    ]
    utils.ensure_states_sent(mocked_controller, expected_states)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expected",
    [
        ("locking", features.CurrentPositionEnum.LOCKING),
        ("unlocking", features.CurrentPositionEnum.UNLOCKING),
        ("not-a-state", features.CurrentPositionEnum.UNKNOWN),
    ],
)
async def test_update_elem(value, expected, mocked_controller):
    await mocked_controller.initialize_elem(lock)
    assert len(mocked_controller.items) == 1
    dev_update = utils.create_devices_from_data("door-lock-TBD.json")[0]
    new_states = [
        HubspaceState(
            **{
                "functionClass": "lock-control",
                "value": value,
                "lastUpdateTime": 0,
                "functionInstance": None,
            }
        ),
    ]
    for state in new_states:
        utils.modify_state(dev_update, state)
    await mocked_controller.update_elem(dev_update)
    dev = mocked_controller.items[0]
    assert dev.position.position == expected
