import os
import requests
import re
from datetime import datetime
from collections import defaultdict

API_KEY = os.getenv("OPENWEATHER_API_KEY")

CITY = "Vienna,AT"
LAT, LON = "48.2082", "16.3738"
UNITS = "metric"
CURRENT_URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units={UNITS}"
FORECAST_URL = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units={UNITS}"

# Emoji icons
emoji_map = {
    "01d": "☀️",
    "01n": "🌙",
    "02d": "🌤️",
    "02n": "☁️",
    "03d": "☁️",
    "03n": "☁️",
    "04d": "☁️",
    "04n": "☁️",
    "09d": "🌧️",
    "09n": "🌧️",
    "10d": "🌦️",
    "10n": "🌦️",
    "11d": "🌩️",
    "11n": "🌩️",
    "13d": "❄️",
    "13n": "❄️",
    "50d": "🌫️",
    "50n": "🌫️",
}

def fetch_weather():
    current = requests.get(CURRENT_URL).json()
    forecast = requests.get(FORECAST_URL).json()
    return current, forecast

def parse_current(current):
    weather = current["weather"][0]
    main = current["main"]
    wind = current["wind"]
    icon = emoji_map.get(weather["icon"], "🌤️")
    
    direction = wind_direction(wind.get("deg", 0))
    
    return {
        "description": weather["description"].capitalize(),
        "icon": icon,
        "temp": round(main["temp"]),
        "feels_like": round(main["feels_like"]),
        "temp_min": round(main["temp_min"]),
        "temp_max": round(main["temp_max"]),
        "humidity": main["humidity"],
        "wind_speed": round(wind.get("speed", 0) * 3.6),  # m/s to km/h
        "wind_dir": direction
    }

def parse_forecast(forecast):
    daily = defaultdict(list)
    for entry in forecast["list"]:
        dt = datetime.fromtimestamp(entry["dt"])
        date = dt.strftime("%a")
        if date == datetime.utcnow().strftime("%a"):
            continue  # skip today
        temp_min = entry["main"]["temp_min"]
        temp_max = entry["main"]["temp_max"]
        icon = entry["weather"][0]["icon"]
        emoji = emoji_map.get(icon, "🌤️")
        description = entry["weather"][0]["main"]

        daily[date].append((temp_min, temp_max, emoji, description))

    # Compress per day forecast
    forecast_summary = []
    for day, entries in list(daily.items())[:5]:
        min_temp = round(min(t[0] for t in entries))
        max_temp = round(max(t[1] for t in entries))
        emoji = entries[0][2]  # Use first entry's emoji
        desc = entries[0][3]
        forecast_summary.append((day, emoji, desc, min_temp, max_temp))

    return forecast_summary

def wind_direction(deg):
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = round(deg / 45) % 8
    return directions[idx]

def update_readme(current, forecast):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    forecast_table = "| Day | Weather | Min / Max |\n|-----|---------|------------|\n"
    for day, icon, desc, tmin, tmax in forecast:
        forecast_table += f"| {day} | {icon} {desc} | {tmin}°C / {tmax}°C |\n"

    new_section = f"""\
## 👋 Hi there!

I'm Jon, a passionate engineer and maker enthusiast based in **Vienna, Austria** 🇦🇹, where we have today:

### {current['icon']} {current['description']} 

🌡️ Temperature: 
* Current: {current['temp']}°C
* Feels like: {current['feels_like']}°C
* Min: {current['temp_min']}°C 
* Max: {current['temp_max']}°C  

💧 Humidity: {current['humidity']}%  
🌬️ Wind: 
* Speed: {current['wind_speed']} km/h 
* Direction: {current['wind_dir']}  

🕒 Updated: {now}

---

### 📅 5-Day Forecast for Vienna

{forecast_table}
"""

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    updated = re.sub(r"(?s)(## 👋 Hi there!.*?)(?=\n## |$)", new_section.strip(), content)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)

if __name__ == "__main__":
    current_data, forecast_data = fetch_weather()
    current = parse_current(current_data)
    forecast = parse_forecast(forecast_data)
    update_readme(current, forecast)
