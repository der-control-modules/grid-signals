import requests
import datetime

def get_pjm_prices(api_key):
    # The base URL for PJM's API
    base_url = "https://api.pjm.com/api/v1/"
    
    # Today's date, which is used to fetch day-ahead prices
    today_date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Real-time prices endpoint; modify as per actual API specification
    real_time_url = f"{base_url}real_time_prices?api_key={api_key}&start_date={today_date}&end_date={today_date}"
    
    # Day-ahead prices endpoint; modify as per actual API specification
    day_ahead_url = f"{base_url}day_ahead_prices?api_key={api_key}&start_date={today_date}&end_date={today_date}"
    
    # Send HTTP GET requests
    real_time_response = requests.get(real_time_url)
    day_ahead_response = requests.get(day_ahead_url)
    
    if real_time_response.status_code == 200 and day_ahead_response.status_code == 200:
        real_time_prices = real_time_response.json()
        day_ahead_prices = day_ahead_response.json()
        return real_time_prices, day_ahead_prices
    else:
        print("Failed to fetch prices")
        return None, None

if __name__ == "__main__":
    # Replace 'your_api_key' with your actual PJM API key
    api_key = 'your_api_key'
    real_time_prices, day_ahead_prices = get_pjm_prices(api_key)

    print("Real-Time Prices:", real_time_prices)
    print("Day-Ahead Prices:", day_ahead_prices)