import urllib.request, json
import numpy as np
import pandas as pd
import datetime

class ComEdPricing:
    BASE_URL = "https://hourlypricing.comed.com/api"

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def fetch_data(self, type='5minutefeed'):
        """ Fetch data from ComEd API based on type. """
        datestart_str = self.start_date.strftime('%Y%m%d%H%M')
        dateend_str = self.end_date.strftime('%Y%m%d%H%M')
        url = f"{self.BASE_URL}?type={type}&datestart={datestart_str}&dateend={dateend_str}"
        
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
        
        return data

    def get_prices_and_times(self, type='5minutefeed'):
        """ Extract prices and timestamps from fetched data based on type. """
        data = self.fetch_data(type)
        prices = [float(item['price']) for item in data if 'price' in item]
        times = [datetime.datetime.fromtimestamp(int(item['millisUTC']) / 1000) for item in data if 'millisUTC' in item]

        return prices, times

    def get_realtime_and_day_ahead(self):
        """ Get both real-time (5-minute feed) and day-ahead prices. """
        realtime_prices, realtime_times = self.get_prices_and_times('5minutefeed')
        day_ahead_prices, day_ahead_times = self.get_prices_and_times('dayahead')  # Assuming 'dayahead' is correct

        return {'realtime': (realtime_prices, realtime_times), 'day_ahead': (day_ahead_prices, day_ahead_times)}

if __name__ == "__main__":
    # Usage
    start_date = datetime.datetime(2021, 1, 1)
    end_date = datetime.datetime(2021, 12, 1)
    comed_pricing = ComEdPricing(start_date, end_date)
    data = comed_pricing.get_realtime_and_day_ahead()

    # Access real-time and day-ahead data
    realtime_prices, realtime_times = data['realtime']
    day_ahead_prices, day_ahead_times = data['day_ahead']