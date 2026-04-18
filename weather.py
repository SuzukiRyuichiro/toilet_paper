import requests

url = "https://api.open-meteo.com/v1/forecast?latitude=35.6918&longitude=139.762&daily=weather_code,temperature_2m_max,temperature_2m_min,rain_sum,showers_sum,precipitation_sum,precipitation_hours,precipitation_probability_max&timezone=Asia%2FTokyo&forecast_days=1"

response = requests.get(url)

print(response.json())
