"""
Imoogle 5.0 Weather Service
Weather information and forecasts using OpenWeatherMap.
"""

import httpx
from typing import Optional, Dict, Any
from dataclasses import dataclass

from app.config import settings


@dataclass
class WeatherData:
    city: str
    country: str
    temperature: float
    feels_like: float
    humidity: int
    description: str
    icon: str
    wind_speed: float
    visibility: int


@dataclass
class ForecastData:
    date: str
    temperature_high: float
    temperature_low: float
    description: str
    icon: str


class WeatherService:
    """
    Weather service using OpenWeatherMap API.
    """
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=15.0)
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    async def close(self):
        await self.http_client.aclose()
    
    async def get_current_weather(
        self,
        city: str = None,
        lat: float = None,
        lon: float = None,
    ) -> Optional[WeatherData]:
        """
        Get current weather for a location.
        
        Args:
            city: City name
            lat: Latitude (alternative to city)
            lon: Longitude (alternative to city)
        
        Returns:
            WeatherData or None if failed
        """
        if not settings.OPENWEATHER_API_KEY:
            return None
        
        params = {
            "appid": settings.OPENWEATHER_API_KEY,
            "units": "metric",
        }
        
        if city:
            params["q"] = city
        elif lat and lon:
            params["lat"] = lat
            params["lon"] = lon
        else:
            return None
        
        try:
            response = await self.http_client.get(
                f"{self.base_url}/weather",
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            
            return WeatherData(
                city=data["name"],
                country=data["sys"]["country"],
                temperature=data["main"]["temp"],
                feels_like=data["main"]["feels_like"],
                humidity=data["main"]["humidity"],
                description=data["weather"][0]["description"].capitalize(),
                icon=data["weather"][0]["icon"],
                wind_speed=data["wind"]["speed"],
                visibility=data.get("visibility", 0),
            )
        except Exception as e:
            print(f"[ImoogleAI] Weather fetch failed: {e}")
            return None
    
    async def get_forecast(
        self,
        city: str = None,
        lat: float = None,
        lon: float = None,
        days: int = 5,
    ) -> list[ForecastData]:
        """
        Get weather forecast for a location.
        
        Args:
            city: City name
            lat/lon: Coordinates
            days: Number of days (max 5)
        
        Returns:
            List of ForecastData
        """
        if not settings.OPENWEATHER_API_KEY:
            return []
        
        params = {
            "appid": settings.OPENWEATHER_API_KEY,
            "units": "metric",
            "cnt": min(days, 5) * 8,  # 8 forecasts per day
        }
        
        if city:
            params["q"] = city
        elif lat and lon:
            params["lat"] = lat
            params["lon"] = lon
        else:
            return []
        
        try:
            response = await self.http_client.get(
                f"{self.base_url}/forecast",
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            
            # Group by day and get high/low
            daily_forecasts = {}
            for item in data.get("list", []):
                date = item["dt_txt"].split()[0]
                if date not in daily_forecasts:
                    daily_forecasts[date] = {
                        "temps": [],
                        "description": item["weather"][0]["description"],
                        "icon": item["weather"][0]["icon"],
                    }
                daily_forecasts[date]["temps"].append(item["main"]["temp"])
            
            forecasts = []
            for date, info in list(daily_forecasts.items())[:days]:
                forecasts.append(ForecastData(
                    date=date,
                    temperature_high=max(info["temps"]),
                    temperature_low=min(info["temps"]),
                    description=info["description"].capitalize(),
                    icon=info["icon"],
                ))
            
            return forecasts
        except Exception as e:
            print(f"[ImoogleAI] Forecast fetch failed: {e}")
            return []
    
    def format_weather(
        self,
        weather: WeatherData,
        use_pidgin: bool = False,
    ) -> str:
        """Format weather data for display."""
        # Weather emoji mapping
        emoji_map = {
            "01": "☀️", "02": "⛅", "03": "☁️", "04": "☁️",
            "09": "🌧️", "10": "🌦️", "11": "⛈️", "13": "❄️", "50": "🌫️",
        }
        emoji = emoji_map.get(weather.icon[:2], "🌡️")
        
        if use_pidgin:
            return f"""{emoji} **Weather for {weather.city}, {weather.country}**

Temperature: {weather.temperature:.1f}°C (e dey feel like {weather.feels_like:.1f}°C)
Weather: {weather.description}
Humidity: {weather.humidity}%
Wind: {weather.wind_speed} m/s

{"E hot well well today o!" if weather.temperature > 30 else "Weather dey somehow manageable." if weather.temperature > 20 else "E cold small today."}"""
        else:
            return f"""{emoji} **Weather for {weather.city}, {weather.country}**

Temperature: {weather.temperature:.1f}°C (feels like {weather.feels_like:.1f}°C)
Conditions: {weather.description}
Humidity: {weather.humidity}%
Wind Speed: {weather.wind_speed} m/s

{"It's quite hot today!" if weather.temperature > 30 else "The weather is pleasant." if weather.temperature > 20 else "It's a bit chilly today."}"""
    
    def format_forecast(
        self,
        forecasts: list[ForecastData],
        city: str,
        use_pidgin: bool = False,
    ) -> str:
        """Format forecast data for display."""
        if not forecasts:
            if use_pidgin:
                return "I no fit find weather forecast for that place o."
            return "I couldn't get the forecast for that location."
        
        emoji_map = {
            "01": "☀️", "02": "⛅", "03": "☁️", "04": "☁️",
            "09": "🌧️", "10": "🌦️", "11": "⛈️", "13": "❄️", "50": "🌫️",
        }
        
        if use_pidgin:
            formatted = f"**Weather Forecast for {city}:**\n\n"
        else:
            formatted = f"**Weather Forecast for {city}:**\n\n"
        
        for day in forecasts:
            emoji = emoji_map.get(day.icon[:2], "🌡️")
            formatted += f"{emoji} **{day.date}**: {day.temperature_low:.0f}°C - {day.temperature_high:.0f}°C\n"
            formatted += f"   {day.description}\n\n"
        
        return formatted


# Singleton instance
weather_service = WeatherService()
