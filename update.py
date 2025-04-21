import requests
from datetime import datetime
import os

API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = "Vienna,AT"
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

def get_weather():
    response = requests.get(URL)
    data = response.json()
    temp = data["main"]["temp"]
    weather = data["weather"][0]["description"].capitalize()
    return temp, weather

def update_readme(temp, weather):
    now = datetime.utcnow().strftime("%Y-%m-%d")
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    new_section = f"### 🌤️ Vienna Weather Forecast ({now})\n**{weather}**, {temp}°C\n"

    updated = re.sub(r"### 🌤️ Vienna Weather Forecast.*?\n.*?\n", new_section, content, flags=re.DOTALL)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)

if __name__ == "__main__":
    import re
    temp, weather = get_weather()
    update_readme(temp, weather)
