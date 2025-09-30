import httpx
from typing import List
from backend.models import GeocodeResult


async def geocode_location(query: str) -> List[GeocodeResult]:
    """Busca ubicaciones usando la API de geocoding de Open-Meteo"""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": query,
        "count": 5,
        "language": "es",
        "format": "json"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if "results" in data:
            for item in data["results"]:
                results.append(GeocodeResult(
                    name=item.get("name", ""),
                    lat=item.get("latitude", 0.0),
                    lon=item.get("longitude", 0.0),
                    country=item.get("country", None),
                    admin1=item.get("admin1", None)
                ))
        
        return results
