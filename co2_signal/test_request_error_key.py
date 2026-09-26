"""A failed request must never print or log the API key.

`requests` embeds the full request URL and headers in the message of a
`RequestException`. The key must not reach stdout, stderr, or a log
record for any of the four request methods.
"""
import logging
from unittest.mock import Mock, patch

import pytest
import requests

from co2_signal.co2_api import ElectricityMapsAPI

MARKER = "SECRET-MARKER-9f3a1c"
URL_WITH_KEY = (
    f"https://api.electricitymap.org/v3/carbon-intensity/latest"
    f"?zone=US-CAL-CISO&auth_token={MARKER}"
)

METHODS = [
    "get_co2_intensity",
    "get_power_breakdown",
    "get_24hr_co2_intensity",
    "get_24hr_power_breakdown",
]


def _http_error():
    response = Mock(status_code=401)
    return requests.exceptions.HTTPError(
        f"401 Client Error: Unauthorized for url: {URL_WITH_KEY}",
        response=response,
    )


def _connection_error():
    return requests.exceptions.ConnectionError(
        "HTTPSConnectionPool(host='api.electricitymap.org', port=443): "
        f"Max retries exceeded with url: {URL_WITH_KEY}"
    )


@pytest.mark.parametrize("method_name", METHODS)
@pytest.mark.parametrize("make_error", [_http_error, _connection_error])
def test_request_failure_never_carries_the_key(method_name, make_error, capsys, caplog):
    api = ElectricityMapsAPI(api_key=MARKER, zone="US-CAL-CISO")
    with patch("co2_signal.co2_api.requests.get", side_effect=make_error()):
        with caplog.at_level(logging.DEBUG):
            result = getattr(api, method_name)()

    assert result is None
    captured = capsys.readouterr()
    assert MARKER not in captured.out
    assert MARKER not in captured.err
    for record in caplog.records:
        assert MARKER not in record.getMessage()
