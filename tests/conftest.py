import pytest
import pytest_asyncio
from aioresponses import aioresponses

from aiohubspace.v1 import HubspaceBridgeV1


@pytest.fixture
def mocked_bridge(mocker):
    mocked_bridge = mocker.Mock(HubspaceBridgeV1, autospec=True)("user", "passwd")
    mocker.patch.object(mocked_bridge, "_account_id", "mocked-account-id")
    mocker.patch.object(mocked_bridge, "request", side_effect=mocker.AsyncMock())
    yield mocked_bridge


@pytest_asyncio.fixture
async def bridge(mocker):
    bridge = HubspaceBridgeV1("user", "passwd")
    mocker.patch.object(bridge, "_account_id", "mocked-account-id")
    mocker.patch.object(bridge, "request", side_effect=mocker.AsyncMock())
    await bridge.initialize()
    yield bridge
    await bridge.close()


@pytest.fixture
def mock_aioresponse():
    with aioresponses() as m:
        yield m
