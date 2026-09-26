"""The API key must travel in the `auth-token` header, never in the URL
or the request params, on every request `ElectricityMapsAPI` makes.
"""
from unittest.mock import Mock, patch

import pytest

from co2_signal.co2_api import ElectricityMapsAPI

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
def test_key_travels_in_auth_header_only(method_name):
    api = ElectricityMapsAPI(api_key=MARKER, zone="US-CAL-CISO")
    with patch(
        "co2_signal.co2_api.requests.get", return_value=_mock_response()
    ) as mock_get:
        getattr(api, method_name)()

    args, kwargs = mock_get.call_args
    url = args[0] if args else kwargs.get("url")
    assert MARKER not in url
    assert MARKER not in str(kwargs.get("params", {}))
    assert kwargs.get("headers") == {"auth-token": MARKER}
