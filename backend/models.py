from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class BoatType(str, Enum):
    VELA_LIGERA = "vela_ligera"
    CRUISER_35 = "cruiser_35"
    CRUISER_35_45 = "cruiser_35_45"
    CATAMARAN = "catamaran"
    DINGHY = "dinghy"
    WINDSURF = "windsurf"


class SkillLevel(str, Enum):
    PRINCIPIANTE = "principiante"
    INTERMEDIO = "intermedio"
    AVANZADO = "avanzado"


class Location(BaseModel):
    name: str
    lat: float
    lon: float
    country: Optional[str] = None
    admin1: Optional[str] = None


class ScoreRequest(BaseModel):
    lat: float
    lon: float
    boat_type: BoatType
    skill: SkillLevel
    date: str
    timezone: str = "Europe/Madrid"


class RawMetrics(BaseModel):
    wind_kn: float
    gust_kn: float
    wave_hs_m: Optional[float] = None
    wave_tp_s: Optional[float] = None
    wave_dir_deg: Optional[float] = None
    wind_dir_deg: Optional[float] = None
    precip_mm_h: float
    temp_c: float


class WindowScore(BaseModel):
    time: str
    score: int
    label: str
    reasons: List[str]
    flags: List[str]
    raw: RawMetrics


class Safety(BaseModel):
    no_go: bool
    why: List[str]


class ScoreResponse(BaseModel):
    location: Location
    windows: List[WindowScore]
    best_window: Optional[WindowScore] = None
    safety: Safety


class GeocodeResult(BaseModel):
    name: str
    lat: float
    lon: float
    country: Optional[str] = None
    admin1: Optional[str] = None


class GeocodeResponse(BaseModel):
    results: List[GeocodeResult]
