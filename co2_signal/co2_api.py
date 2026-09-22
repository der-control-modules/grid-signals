import requests
from datetime import datetime, timedelta

class ElectricityMapsAPI:
    def __init__(self, api_key, zone):
        self.api_key = api_key
        self.zone = zone
        self.base_url = 'https://api.electricitymap.org/v3'

    def get_co2_intensity(self):
        """Get the current CO2 intensity for a specified zone."""
        url = f'{self.base_url}/carbon-intensity/latest'
        params = {'zone': self.zone, 'auth_token': self.api_key}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f'error: {str(e)}')
            return None

    def get_power_breakdown(self):
        """Get the current power generation breakdown for a specified zone."""
        url = f'{self.base_url}/power-breakdown/latest'
        params = {'zone': self.zone, 'auth_token': self.api_key}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f'error: {str(e)}')
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
            'auth_token': self.api_key
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f'error: {str(e)}')
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
            'auth_token': self.api_key
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f'error: {str(e)}')
            return None
        
