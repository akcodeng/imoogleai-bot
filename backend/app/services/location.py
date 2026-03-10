"""
Imoogle 5.0 Location Service
Detect user location from IP for personalization.
"""

import httpx
from typing import Optional, Dict, Any
from dataclasses import dataclass

from app.config import settings


@dataclass
class LocationData:
    ip: str
    city: str
    region: str
    country: str
    country_code: str
    timezone: str
    latitude: float
    longitude: float


class LocationService:
    """
    Location detection service using IP geolocation.
    Supports: IPInfo, ip-api.com (fallback)
    """
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=10.0)
    
    async def close(self):
        await self.http_client.aclose()
    
    async def get_location(self, ip: str = None) -> Optional[LocationData]:
        """
        Get location data from IP address.
        
        Args:
            ip: IP address (if None, uses request IP)
        
        Returns:
            LocationData or None if failed
        """
        # Try IPInfo first
        if settings.IPINFO_TOKEN:
            try:
                return await self._ipinfo_lookup(ip)
            except Exception as e:
                print(f"[ImoogleAI] IPInfo lookup failed: {e}")
        
        # Fallback to ip-api.com (free, no API key)
        try:
            return await self._ipapi_lookup(ip)
        except Exception as e:
            print(f"[ImoogleAI] ip-api lookup failed: {e}")
        
        return None
    
    async def _ipinfo_lookup(self, ip: str = None) -> LocationData:
        """Lookup using IPInfo."""
        url = f"https://ipinfo.io/{ip or 'json'}"
        if not ip:
            url = "https://ipinfo.io/json"
        
        params = {"token": settings.IPINFO_TOKEN}
        
        response = await self.http_client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Parse location
        loc = data.get("loc", "0,0").split(",")
        
        return LocationData(
            ip=data.get("ip", ""),
            city=data.get("city", "Unknown"),
            region=data.get("region", "Unknown"),
            country=data.get("country", "Unknown"),
            country_code=data.get("country", ""),
            timezone=data.get("timezone", "UTC"),
            latitude=float(loc[0]) if len(loc) > 0 else 0,
            longitude=float(loc[1]) if len(loc) > 1 else 0,
        )
    
    async def _ipapi_lookup(self, ip: str = None) -> LocationData:
        """Lookup using ip-api.com (free)."""
        url = f"http://ip-api.com/json/{ip or ''}"
        
        response = await self.http_client.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "success":
            raise Exception(f"ip-api error: {data.get('message')}")
        
        return LocationData(
            ip=data.get("query", ""),
            city=data.get("city", "Unknown"),
            region=data.get("regionName", "Unknown"),
            country=data.get("country", "Unknown"),
            country_code=data.get("countryCode", ""),
            timezone=data.get("timezone", "UTC"),
            latitude=data.get("lat", 0),
            longitude=data.get("lon", 0),
        )
    
    def get_localized_greeting(
        self,
        location: LocationData,
        user_name: str = "friend",
    ) -> str:
        """Get a localized greeting based on location."""
        country = location.country_code.upper()
        
        greetings = {
            "NG": f"How far {user_name}! I see say you dey {location.city}, Nigeria. Na your city be that! 🇳🇬",
            "GH": f"Akwaaba {user_name}! I see you're in {location.city}, Ghana. Welcome! 🇬🇭",
            "KE": f"Jambo {user_name}! Looks like you're in {location.city}, Kenya. Karibu! 🇰🇪",
            "ZA": f"Howzit {user_name}! I see you're in {location.city}, South Africa. Lekker! 🇿🇦",
            "US": f"Hey {user_name}! I see you're in {location.city}, USA. What's up! 🇺🇸",
            "GB": f"Hello {user_name}! I see you're in {location.city}, UK. Lovely to meet you! 🇬🇧",
            "BR": f"Olá {user_name}! I see you're in {location.city}, Brazil. Bem-vindo! 🇧🇷",
            "IN": f"Namaste {user_name}! I see you're in {location.city}, India. Welcome! 🇮🇳",
        }
        
        default = f"Hello {user_name}! I see you're based in {location.city}, {location.country}. Nice to meet you!"
        
        return greetings.get(country, default)
    
    def should_use_pidgin(self, location: LocationData) -> bool:
        """Determine if pidgin should be used based on location."""
        # Use pidgin for Nigeria
        return location.country_code.upper() == "NG"
    
    def get_country_specific_features(
        self,
        location: LocationData,
    ) -> Dict[str, Any]:
        """Get features available for a country."""
        country = location.country_code.upper()
        
        # Nigeria has all features
        if country == "NG":
            return {
                "imoogle_pay": True,
                "p2p_transfer": True,
                "deposit": True,
                "withdrawal": True,
                "imocoin": True,
                "local_bank_transfer": True,
                "currency": "NGN",
                "currency_symbol": "₦",
            }
        
        # Other African countries - coming soon
        african_countries = ["GH", "KE", "ZA", "EG", "TZ", "UG", "RW", "SN", "CI"]
        if country in african_countries:
            return {
                "imoogle_pay": False,
                "p2p_transfer": False,
                "deposit": False,
                "withdrawal": False,
                "imocoin": False,
                "coming_soon": True,
                "message": f"Imoogle Pay is coming soon to {location.country}! Stay tuned.",
            }
        
        # Other countries - not available
        return {
            "imoogle_pay": False,
            "p2p_transfer": False,
            "deposit": False,
            "withdrawal": False,
            "imocoin": False,
            "coming_soon": False,
            "message": "Imoogle Pay is currently only available in Nigeria. We're expanding soon!",
        }


# Singleton instance
location_service = LocationService()
