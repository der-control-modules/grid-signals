import requests
from datetime import datetime, timedelta
from urllib.parse import urlparse

# Bounds each connect and each socket read; a server that stays connected
# and trickles bytes forever is not bounded by this alone.
REQUEST_TIMEOUT_SECONDS = 10


def _log_request_error(endpoint: str, error: requests.RequestException) -> None:
    # str(error) embeds the full request URL, so only the endpoint (no
    # query string) and the status or error type are safe to print here.
    status = error.response.status_code if error.response is not None else None
    detail = f'status {status}' if status is not None else type(error).__name__
    print(f'error: request to {endpoint} failed: {detail}')


class _HostScopedAuthSession(requests.Session):
    """`Session.rebuild_auth` only strips `Authorization` on a redirect
    to a new host; our key travels in `auth-token`, so it needs the same
    treatment. A same-host redirect keeps the header.
    """

    def rebuild_auth(self, prepared_request, response):
        super().rebuild_auth(prepared_request, response)
        headers = prepared_request.headers
        if 'auth-token' not in headers:
            return
        old_host = urlparse(response.request.url).hostname
        new_host = urlparse(prepared_request.url).hostname
        if old_host != new_host:
            del headers['auth-token']


class ElectricityMapsAPI:
    def __init__(self, api_key, zone):
        self.api_key = api_key
        self.zone = zone
        self.base_url = 'https://api.electricitymap.org/v3'
        self._session = _HostScopedAuthSession()

    def _auth_headers(self) -> dict[str, str]:
        # Vendor docs authenticate every endpoint but /zones this way; see #7.
        return {'auth-token': self.api_key}

    def get_co2_intensity(self):
        """Get the current CO2 intensity for a specified zone."""
        url = f'{self.base_url}/carbon-intensity/latest'
        params = {'zone': self.zone}
        try:
            response = self._session.get(
                url, params=params, headers=self._auth_headers(),
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            _log_request_error(url, e)
            return None

    def get_power_breakdown(self):
        """Get the current power generation breakdown for a specified zone."""
        url = f'{self.base_url}/power-breakdown/latest'
        params = {'zone': self.zone}
        try:
            response = self._session.get(
                url, params=params, headers=self._auth_headers(),
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            _log_request_error(url, e)
            return None

    def get_24hr_co2_intensity(self):
        """Get the CO2 intensity for a specified zone over the past 24 hours."""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        url = f'{self.base_url}/carbon-intensity/history'
        params = {
            'zone': self.zone,
            'start': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'end': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        }
        try:
            response = self._session.get(
                url, params=params, headers=self._auth_headers(),
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            _log_request_error(url, e)
            return None

    def get_24hr_power_breakdown(self):
        """Get the power generation breakdown for a specified zone over the past 24 hours."""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        url = f'{self.base_url}/power-breakdown/history'
        params = {
            'zone': self.zone,
            'start': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'end': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        }
        try:
            response = self._session.get(
                url, params=params, headers=self._auth_headers(),
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            _log_request_error(url, e)
            return None
        
