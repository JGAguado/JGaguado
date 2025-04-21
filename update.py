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

# Map OpenWeather icon codes to Material Design Icons (MDI)
mdi_icon_map = {
    "01d": "weather-sunny",
    "01n": "weather-night",
    "02d": "weather-partly-cloudy",
    "02n": "weather-night-partly-cloudy",
    "03d": "weather-cloudy",
    "03n": "weather-cloudy",
    "04d": "weather-cloudy",
    "04n": "weather-cloudy",
    "09d": "weather-pouring",
    "09n": "weather-pouring",
    "10d": "weather-rainy",
    "10n": "weather-rainy",
    "11d": "weather-lightning",
    "11n": "weather-lightning",
    "13d": "weather-snowy",
    "13n": "weather-snowy",
    "50d": "weather-fog",
    "50n": "weather-fog",
}

def fetch_weather():
    current = requests.get(CURRENT_URL).json()
    forecast = requests.get(FORECAST_URL).json()
    return current, forecast

def parse_current(current):
    weather = current["weather"][0]
    main = current["main"]
    wind = current["wind"]
    icon = mdi_icon_map.get(weather["icon"], "weather-cloudy")
    
    direction = wind_direction(wind.get("deg", 0))
    
    return {
        "description": weather["description"].capitalize(),
        "icon": icon,
        "temp": round(main["temp"]),
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
        temp_min = entry["main"]["temp_min"]
        temp_max = entry["main"]["temp_max"]
        icon = entry["weather"][0]["icon"]
        mdi_icon = mdi_icon_map.get(icon, "weather-cloudy")
        description = entry["weather"][0]["main"]

        daily[date].append((temp_min, temp_max, mdi_icon, description))

    # Compress per day forecast
    forecast_summary = []
    for day, entries in list(daily.items())[:5]:
        min_temp = round(min(t[0] for t in entries))
        max_temp = round(max(t[1] for t in entries))
        mdi_icon = entries[0][2]  # Use first entry's icon for simplicity
        desc = entries[0][3]
        forecast_summary.append((day, mdi_icon, desc, min_temp, max_temp))

    return forecast_summary

def wind_direction(deg):
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = round(deg / 45) % 8
    return directions[idx]

def update_readme(current, forecast):
    now = datetime.utcnow().strftime("%Y-%m-%d")
    
    icon_url = f"https://raw.githubusercontent.com/Templarian/MaterialDesign/master/icons/svg/{current['icon']}.svg"
    
    forecast_table = "| Day | Weather | Min / Max |\n|-----|---------|------------|\n"
    for day, icon, desc, tmin, tmax in forecast:
        url = f"https://raw.githubusercontent.com/Templarian/MaterialDesign/master/icons/svg/{icon}.svg"
        forecast_table += f"| {day} | ![{icon}]({url}) {desc} | {tmin}°C / {tmax}°C |\n"

    new_section = f"""\
## 👋 Hi there!

I'm Jon, a passionate engineer and maker enthusiast based in **Vienna, Austria** 🇦🇹.

### 🌤️ Weather in Vienna – {now}

![{current['icon']}]({icon_url})  
**{current['description']}**, {current['temp']}°C (min {current['temp_min']}°C, max {current['temp_max']}°C)  
💧 Humidity: {current['humidity']}%  
🌬️ Wind: {current['wind_speed']} km/h from {current['wind_dir']}

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
