import requests
from backend.config import OPENWEATHER_API_KEY
def get_current_weather(city:str):
    url=f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    r=requests.get(url,timeout=30)
    return r.json()
