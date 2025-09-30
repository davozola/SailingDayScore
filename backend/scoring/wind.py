from backend.models import BoatType, SkillLevel
from typing import Tuple, Dict


WIND_MATRIX: Dict[BoatType, Dict[SkillLevel, Tuple[float, float]]] = {
    BoatType.VELA_LIGERA: {
        SkillLevel.PRINCIPIANTE: (6.0, 12.0),
        SkillLevel.INTERMEDIO: (8.0, 15.0),
        SkillLevel.AVANZADO: (10.0, 18.0)
    },
    BoatType.CRUISER_35: {
        SkillLevel.PRINCIPIANTE: (8.0, 14.0),
        SkillLevel.INTERMEDIO: (10.0, 18.0),
        SkillLevel.AVANZADO: (12.0, 22.0)
    },
    BoatType.CRUISER_35_45: {
        SkillLevel.PRINCIPIANTE: (8.0, 16.0),
        SkillLevel.INTERMEDIO: (10.0, 20.0),
        SkillLevel.AVANZADO: (12.0, 24.0)
    },
    BoatType.CATAMARAN: {
        SkillLevel.PRINCIPIANTE: (8.0, 14.0),
        SkillLevel.INTERMEDIO: (10.0, 18.0),
        SkillLevel.AVANZADO: (12.0, 22.0)
    },
    BoatType.DINGHY: {
        SkillLevel.PRINCIPIANTE: (7.0, 12.0),
        SkillLevel.INTERMEDIO: (10.0, 16.0),
        SkillLevel.AVANZADO: (12.0, 20.0)
    },
    BoatType.WINDSURF: {
        SkillLevel.PRINCIPIANTE: (7.0, 12.0),
        SkillLevel.INTERMEDIO: (10.0, 16.0),
        SkillLevel.AVANZADO: (12.0, 20.0)
    }
}


def score_wind(wind_kn: float, boat_type: BoatType, skill: SkillLevel) -> Tuple[float, str]:
    """
    Calcula puntuación base por viento.
    Retorna (puntos, razón)
    """
    optimal_range = WIND_MATRIX[boat_type][skill]
    min_optimal, max_optimal = optimal_range
    
    if min_optimal <= wind_kn <= max_optimal:
        score = 60.0
        reason = f"Viento {wind_kn:.1f} kn en rango óptimo"
    else:
        if wind_kn < min_optimal:
            delta = min_optimal - wind_kn
            score = max(60.0 - (delta * 3.0), 30.0)
            reason = f"Viento {wind_kn:.1f} kn (flojo, óptimo {min_optimal:.0f}-{max_optimal:.0f} kn)"
        else:
            delta = wind_kn - max_optimal
            score = max(60.0 - (delta * 3.0), 30.0)
            reason = f"Viento {wind_kn:.1f} kn (fuerte, óptimo {min_optimal:.0f}-{max_optimal:.0f} kn)"
    
    return score, reason


def score_gust_factor(wind_kn: float, gust_kn: float) -> Tuple[float, str]:
    """
    Penaliza por factor de rachas.
    Retorna (penalización, flag opcional)
    """
    if wind_kn < 1.0:
        return 0.0, ""
    
    gust_factor = gust_kn / wind_kn
    
    if gust_factor <= 1.2:
        return 0.0, ""
    elif gust_factor <= 1.35:
        return -5.0, f"Rachas moderadas ({gust_kn:.1f} kn)"
    elif gust_factor <= 1.5:
        return -10.0, f"Rachas elevadas ({gust_kn:.1f} kn)"
    else:
        return -20.0, f"Rachas muy fuertes ({gust_kn:.1f} kn)"
