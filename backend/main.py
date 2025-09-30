from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from backend.models import (
    ScoreRequest, ScoreResponse, GeocodeResponse, 
    Location, WindowScore, Safety, RawMetrics
)
from backend.services.geocode import geocode_location
from backend.services.openmeteo import fetch_weather_data, sample_hourly_to_3h
from backend.services.marine import fetch_marine_data, sample_marine_to_3h
from backend.scoring.combined import create_window_score, check_no_go
from typing import Optional, Dict, Tuple
from datetime import datetime
import asyncio


app = FastAPI(title="Sailing Day Score API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


CACHE: Dict[str, Tuple[Tuple, float]] = {}
CACHE_TTL = 600.0


def get_cache_key(lat: float, lon: float, date: str) -> str:
    return f"{lat:.2f}_{lon:.2f}_{date}"


def clean_expired_cache():
    """Limpia entradas expiradas del cache"""
    now = datetime.now().timestamp()
    expired_keys = [key for key, (_, timestamp) in CACHE.items() if now - timestamp >= CACHE_TTL]
    for key in expired_keys:
        del CACHE[key]


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/geocode", response_model=GeocodeResponse)
async def geocode(q: str = Query(..., description="Nombre de ubicación")):
    try:
        results = await geocode_location(q)
        return GeocodeResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en geocoding: {str(e)}")


@app.post("/api/score", response_model=ScoreResponse)
async def score(request: ScoreRequest):
    try:
        clean_expired_cache()
        
        cache_key = get_cache_key(request.lat, request.lon, request.date)
        now = datetime.now().timestamp()
        
        if cache_key in CACHE:
            cached_data, timestamp = CACHE[cache_key]
            if now - timestamp < CACHE_TTL:
                weather_data, marine_data = cached_data
            else:
                del CACHE[cache_key]
                weather_data, marine_data = await asyncio.gather(
                    fetch_weather_data(request.lat, request.lon, request.date, request.timezone),
                    fetch_marine_data(request.lat, request.lon, request.date, request.timezone)
                )
                CACHE[cache_key] = ((weather_data, marine_data), now)
        else:
            weather_data, marine_data = await asyncio.gather(
                fetch_weather_data(request.lat, request.lon, request.date, request.timezone),
                fetch_marine_data(request.lat, request.lon, request.date, request.timezone)
            )
            CACHE[cache_key] = ((weather_data, marine_data), now)
        
        if "hourly" not in weather_data:
            raise HTTPException(status_code=500, detail="No se pudieron obtener datos meteorológicos")
        
        weather_samples = sample_hourly_to_3h(weather_data["hourly"])
        marine_samples = []
        if marine_data and "hourly" in marine_data:
            marine_samples = sample_marine_to_3h(marine_data["hourly"])
        
        windows = []
        for i, w_sample in enumerate(weather_samples):
            wave_hs = None
            wave_tp = None
            wave_dir = None
            
            if i < len(marine_samples):
                m_sample = marine_samples[i]
                wave_hs = m_sample.get("wave_height")
                wave_tp = m_sample.get("wave_period")
                wave_dir = m_sample.get("wave_direction")
            
            metrics = RawMetrics(
                wind_kn=w_sample["wind_speed"] * 1.94384,
                gust_kn=w_sample["wind_gust"] * 1.94384,
                wave_hs_m=wave_hs,
                wave_tp_s=wave_tp,
                wave_dir_deg=wave_dir,
                wind_dir_deg=w_sample["wind_direction"],
                precip_mm_h=w_sample["precipitation"],
                temp_c=w_sample["temperature"]
            )
            
            window = create_window_score(
                w_sample["time"],
                metrics,
                request.boat_type,
                request.skill
            )
            windows.append(window)
        
        best_window = None
        if windows:
            best_window = max(windows, key=lambda w: w.score)
        
        no_go_checks = [check_no_go(w.raw, request.skill) for w in windows]
        any_no_go = any(check[0] for check in no_go_checks)
        no_go_reasons = []
        if any_no_go:
            for check in no_go_checks:
                no_go_reasons.extend(check[1])
            no_go_reasons = list(set(no_go_reasons))
        
        location = Location(
            name=f"Lat {request.lat:.2f}, Lon {request.lon:.2f}",
            lat=request.lat,
            lon=request.lon
        )
        
        return ScoreResponse(
            location=location,
            windows=windows,
            best_window=best_window,
            safety=Safety(no_go=any_no_go, why=no_go_reasons)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular score: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
