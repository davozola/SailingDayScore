import httpx
from typing import Dict, List, Optional
from datetime import datetime, timedelta


async def fetch_marine_data(lat: float, lon: float, date: str, timezone: str, days: int = 5) -> Optional[Dict]:
    """Obtiene datos marinos de Open-Meteo Marine API"""
    url = "https://marine-api.open-meteo.com/v1/marine"
    
    start_date = datetime.fromisoformat(date)
    end_date = start_date + timedelta(days=days - 1)
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "wave_height,wave_direction,wave_period",
        "timezone": timezone,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except (httpx.HTTPError, httpx.RequestError):
        return None


def sample_marine_to_3h(hourly_data: Dict, start_hour: int = 0) -> List[Dict]:
    """Samplea datos marinos horarios a intervalos de 3 horas"""
    times = hourly_data.get("time", [])
    wave_heights = hourly_data.get("wave_height", [])
    wave_dirs = hourly_data.get("wave_direction", [])
    wave_periods = hourly_data.get("wave_period", [])
    
    samples = []
    for i in range(start_hour, len(times), 3):
        if i >= len(wave_heights):
            break
        
        samples.append({
            "time": times[i],
            "wave_height": wave_heights[i],
            "wave_direction": wave_dirs[i],
            "wave_period": wave_periods[i]
        })
    
    return samples
