import json

class PriceProfileGenerator:
    def __init__(self, filename):
        self.data = self.load_prices_from_json(filename)
    
    def load_prices_from_json(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
        return data
    
    def generate_standard_profile(self, peak_prices, off_peak_prices):
        profile = []
        for hour in range(24):
            if any(start <= hour < end for start, end, _ in peak_prices):
                profile.append(next(price for start, end, price in peak_prices if start <= hour < end))
            else:
                profile.append(next(price for start, end, price in off_peak_prices if start <= hour < end))
        return profile
    
    def generate_critical_profile(self, critical_peak_prices, peak_prices, off_peak_prices):
        profile = []
        for hour in range(24):
            if any(start <= hour < end for start, end, _ in critical_peak_prices):
                profile.append(next(price for start, end, price in critical_peak_prices if start <= hour < end))
            elif any(start <= hour < end for start, end, _ in peak_prices):
                profile.append(next(price for start, end, price in peak_prices if start <= hour < end))
            else:
                profile.append(next(price for start, end, price in off_peak_prices if start <= hour < end))
        return profile
    
    def generate_seasonal_profile(self, summer_peak_prices, summer_off_peak_prices, winter_peak_prices, winter_off_peak_prices, month):
        if month in [6, 7, 8]:  # Summer season
            return self.generate_standard_profile(summer_peak_prices, summer_off_peak_prices)
        else:  # Winter season
            return self.generate_standard_profile(winter_peak_prices, winter_off_peak_prices)
    
    def generate_profile(self, type_of_tou, month=None):
        if type_of_tou.lower() == 'standard':
            print("Standard pricing (peak and off-peak) will be used.")
            peak_prices = self.data[type_of_tou.lower()]['peak_prices']
            off_peak_prices = self.data[type_of_tou.lower()]['off_peak_prices']
            profile = self.generate_standard_profile(peak_prices, off_peak_prices)
        elif type_of_tou.lower() == 'critical':
            critical_peak_prices = self.data[type_of_tou.lower()]['critical_peak_prices']
            peak_prices = self.data[type_of_tou.lower()]['peak_prices']
            off_peak_prices = self.data[type_of_tou.lower()]['off_peak_prices']
            profile = self.generate_critical_profile(critical_peak_prices, peak_prices, off_peak_prices)
        elif type_of_tou.lower() == 'seasonal':
            summer_peak_prices = self.data[type_of_tou.lower()]['summer_peak_prices']
            summer_off_peak_prices = self.data[type_of_tou.lower()]['summer_off_peak_prices']
            winter_peak_prices = self.data[type_of_tou.lower()]['winter_peak_prices']
            winter_off_peak_prices = self.data[type_of_tou.lower()]['winter_off_peak_prices']
            profile = self.generate_seasonal_profile(summer_peak_prices, summer_off_peak_prices, winter_peak_prices, winter_off_peak_prices, month)
        else:
            print("Standard pricing (peak and off-peak) will be used.")
            peak_prices = [(0, 6, 0.20), (18, 24, 0.20)]
            off_peak_prices = [(6, 18, 0.10)]
            profile = self.generate_standard_profile(peak_prices, off_peak_prices)
        
        return profile

def main():
    filename = "OptSimulation/grid_signals/prices/TOU/tou.json"
    generator = PriceProfileGenerator(filename)
    
    type_of_tou = input("Enter the type of TOU prices (standard, critical, seasonal): ")
    
    if type_of_tou.lower() == 'seasonal':
        month = int(input("Enter the month (1-12): "))
        profile = generator.generate_profile(type_of_tou, month)
    else:
        profile = generator.generate_profile(type_of_tou)
        
    print("Generated 24-hour price profile:")
    for hour, price in enumerate(profile):
        print("Hour {}: ${}/kWh".format(hour, price))

if __name__ == "__main__":
    main()
