import pytest
from aioresponses import aioresponses

from aiohubspace.v1 import HubspaceBridgeV1


@pytest.fixture
def mocked_bridge(mocker):
    mocked_bridge = mocker.Mock(HubspaceBridgeV1, autospec=True)("user", "passwd")
    mocker.patch.object(mocked_bridge, "_account_id", "mocked-account-id")
    mocker.patch.object(mocked_bridge, "request", side_effect=mocker.AsyncMock())
    yield mocked_bridge


@pytest.fixture
def mock_aioresponse():
    with aioresponses() as m:
        yield m
