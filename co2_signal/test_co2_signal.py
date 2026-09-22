import requests
from datetime import datetime, timedelta
import json

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
            return {'error': str(e)}

    def get_power_breakdown(self):
        """Get the current power generation breakdown for a specified zone."""
        url = f'{self.base_url}/power-breakdown/latest'
        params = {'zone': self.zone, 'auth_token': self.api_key}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {'error': str(e)}

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
            return {'error': str(e)}

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
            return {'error': str(e)}
        
    # Function to shift all entries by 24 hours
    def shift_24hr_co2(self):
        data = self.get_24hr_co2_intensity()
        new_history = []
        for entry in data['history']:
            new_datetime = datetime.fromisoformat(entry['datetime'].replace('Z', '+00:00')) + timedelta(hours=24)
            new_entry = {
                'datetime': new_datetime.isoformat() + 'Z',  # Adjust back to UTC format with 'Z'
                'carbonIntensity': entry['carbonIntensity']
            }
            new_history.append(new_entry)
        return new_history
    
    # Function to shift all entries by 24 hours
    def shift_24hr_powerbreakdown(self):
        data = self.get_24hr_power_breakdown()
        new_history = []
        for entry in data['history']:
            new_datetime = datetime.fromisoformat(entry['datetime'].replace('Z', '+00:00')) + timedelta(hours=24)
            new_entry = {
                'datetime': new_datetime.isoformat() + 'Z',  # Adjust back to UTC format with 'Z'
                'powerConsumptionBreakdown': entry['powerConsumptionBreakdown'].copy()
            }
            new_history.append(new_entry)
        return new_history

# Shift the historical data by 24 hours


# Example usage
api_key = '9t9jNatVh8KUN'  # Example key
zone = 'US-CAL-CISO'
api = ElectricityMapsAPI(api_key, zone)


# Test the functions for current and 24-hour data

co2_intensity = api.get_co2_intensity()
print("co2_intensity:", co2_intensity)
power_breakdown = api.get_power_breakdown()
# co2_intensity_24hr = api.get_24hr_co2_intensity()
# print("*************************************************")
# print("co2_intensity_24hr:", co2_intensity_24hr)
# # print("*************************************************")

#print(json.dumps(api.shift_24hr_co2(), indent=2))
print(json.dumps(api.shift_24hr_powerbreakdown(), indent=2))
#print("Current CO2 Intensity:", co2_intensity)
#print("Current Power Breakdown:", power_breakdown)
# print("*************************************************")
# print("co2_intensity_24hr:", co2_intensity_24hr)
# print("*************************************************")
# print("power_breakdown_24hr:", power_breakdown_24hr)
