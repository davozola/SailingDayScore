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


def score_gust_factor(wind_kn: float, gust_kn: float, skill: SkillLevel) -> Tuple[float, str]:
    """
    Penaliza por factor de rachas según nivel de experiencia.
    Retorna (penalización, flag opcional)
    """
    if wind_kn < 1.0:
        return 0.0, ""
    
    gust_factor = gust_kn / wind_kn
    percentage = int((gust_factor - 1.0) * 100)
    
    # Factores de penalización según nivel
    skill_multipliers = {
        SkillLevel.PRINCIPIANTE: 1.0,    # Penalización completa
        SkillLevel.INTERMEDIO: 0.7,       # 70% de penalización
        SkillLevel.AVANZADO: 0.4          # 40% de penalización
    }
    multiplier = skill_multipliers[skill]
    
    if gust_factor <= 1.2:
        return 0.0, ""
    elif gust_factor <= 1.35:
        penalty = -5.0 * multiplier
        flag = f"Rachas moderadas +{percentage}% ({gust_kn:.1f} kn): mayor esfuerzo físico" if gust_kn >= 12.0 else ""
        return penalty, flag
    elif gust_factor <= 1.5:
        penalty = -10.0 * multiplier
        flag = f"Rachas elevadas +{percentage}% ({gust_kn:.1f} kn): riesgo de orzadas y escoras bruscas" if gust_kn >= 15.0 else ""
        return penalty, flag
    elif gust_factor <= 1.7:
        penalty = -15.0 * multiplier
        flag = f"Rachas muy fuertes +{percentage}% ({gust_kn:.1f} kn): velas difíciles de controlar, posible daño al aparejo" if gust_kn >= 18.0 else ""
        return penalty, flag
    else:
        penalty = -20.0 * multiplier
        flag = f"Rachas extremas +{percentage}% ({gust_kn:.1f} kn): alto riesgo de volcada, control muy difícil" if gust_kn >= 20.0 else ""
        return penalty, flag
