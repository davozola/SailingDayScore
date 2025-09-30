import httpx
from typing import Dict, List
from datetime import datetime, timedelta


async def fetch_weather_data(lat: float, lon: float, date: str, timezone: str, days: int = 5) -> Dict:
    """Obtiene datos de forecast de Open-Meteo"""
    url = "https://api.open-meteo.com/v1/forecast"
    
    start_date = datetime.fromisoformat(date)
    end_date = start_date + timedelta(days=days - 1)
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "windspeed_10m,windgusts_10m,temperature_2m,precipitation,winddirection_10m",
        "timezone": timezone,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


def sample_hourly_to_3h(hourly_data: Dict, start_hour: int = 0) -> List[Dict]:
    """Samplea datos horarios a intervalos de 3 horas"""
    times = hourly_data.get("time", [])
    wind_speeds = hourly_data.get("windspeed_10m", [])
    wind_gusts = hourly_data.get("windgusts_10m", [])
    temps = hourly_data.get("temperature_2m", [])
    precips = hourly_data.get("precipitation", [])
    wind_dirs = hourly_data.get("winddirection_10m", [])
    
    samples = []
    for i in range(start_hour, len(times), 3):
        if i >= len(wind_speeds):
            break
        
        samples.append({
            "time": times[i],
            "wind_speed": wind_speeds[i],
            "wind_gust": wind_gusts[i],
            "temperature": temps[i],
            "precipitation": precips[i],
            "wind_direction": wind_dirs[i]
        })
    
    return samples
