import json

class PriceProfileGenerator:
    def __init__(self, tou_config):
        self.tou_config = tou_config
    
    def generate_standard_profile(self):
        profile = []
        # Define price ranges based on the TOU configuration
        peak_prices = [(start, end, self.tou_config['pricing']['on-peak']) for start, end in self.tou_config['interval']['on-peak']]
        mid_peak_intervals = self.tou_config['interval']['mid-peak']
        if all(isinstance(item, list) and len(item) == 2 for item in mid_peak_intervals):
            mid_peak_prices = [(start, end, self.tou_config['pricing']['mid-peak']) for start, end in mid_peak_intervals]
        else:
            raise ValueError("Interval data is not properly formatted.")
        off_peak_prices = [(start, end, self.tou_config['pricing']['off-peak']) for start, end in self.tou_config['interval']['off-peak']]
        for hour in range(24):  # Adjusting range to include hour 23
            # Debugging line, assuming there's a default value that makes sense for your context
            print(next((price for start, end, price in off_peak_prices if start <= hour < end), 'No price match'))

            if any(start <= hour < end for start, end, _ in peak_prices):
                # Append peak price for this hour if it exists, else default value
                profile.append(next((price for start, end, price in peak_prices if start <= hour < end),
                                    self.tou_config['pricing']['on-peak']))
            elif any(start <= hour < end for start, end, _ in mid_peak_prices):
                # Append mid-peak price for this hour if it exists, else default value
                profile.append(next((price for start, end, price in mid_peak_prices if start <= hour < end),
                                    self.tou_config['pricing']['mid-peak']))
            else:
                # Append off-peak price for this hour if it exists, else default value
                profile.append(next((price for start, end, price in off_peak_prices if start <= hour < end),
                                    self.tou_config['pricing']['off-peak']))
        return profile

    def generate_profile(self):
        print("Generating standard TOU pricing profile.")
        return self.generate_standard_profile()