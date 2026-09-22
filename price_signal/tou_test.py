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

if __name__ == "__main__":
    # Example TOU configuration JSON, structured according to your input
    tou_config = {
        "type_of_tou_pricing": "standard",
        "TOU_pricing": {
                "interval":{"off-peak":[[0, 7], [21, 23]], "mid-peak":[[7, 10], [11, 12], [17, 21]] , "on-peak":[[10, 11], [12, 17]]},
                "pricing":{"off-peak": 4.675, "mid-peak": 9.083, "on-peak": 15.925}
                }
    }

    # Creating an instance of the PriceProfileGenerator with the provided TOU config
    generator = PriceProfileGenerator(tou_config['TOU_pricing'])
    profile = generator.generate_profile()
    print(profile)
