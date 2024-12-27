import pytest

from aiohubspace.v1 import HubSpaceBridgeV1


@pytest.fixture
def mocked_bridge(mocker):
    mocked_bridge = mocker.Mock(HubSpaceBridgeV1, autospec=True)("user", "passwd")
    mocker.patch.object(mocked_bridge, "_account_id", "mocked-account-id")
    mocker.patch.object(mocked_bridge, "request", side_effect=mocker.AsyncMock())
    yield mocked_bridge
