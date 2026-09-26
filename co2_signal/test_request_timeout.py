"""Every request must carry a timeout, so a stalled server cannot hang
the caller indefinitely.
"""
from unittest.mock import Mock, patch

import pytest

from co2_signal.co2_api import REQUEST_TIMEOUT_SECONDS, ElectricityMapsAPI

MARKER = "SECRET-MARKER-9f3a1c"

METHODS = [
    "get_co2_intensity",
    "get_power_breakdown",
    "get_24hr_co2_intensity",
    "get_24hr_power_breakdown",
]


def _mock_response():
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"ok": True}
    return response


@pytest.mark.parametrize("method_name", METHODS)
def test_request_has_a_timeout(method_name):
    api = ElectricityMapsAPI(api_key=MARKER, zone="US-CAL-CISO")
    with patch(
        "co2_signal.co2_api._HostScopedAuthSession.get", return_value=_mock_response()
    ) as mock_get:
        getattr(api, method_name)()

    _, kwargs = mock_get.call_args
    assert kwargs.get("timeout") == REQUEST_TIMEOUT_SECONDS
