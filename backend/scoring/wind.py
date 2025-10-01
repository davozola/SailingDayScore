from backend.models import BoatType, SkillLevel
from typing import Tuple, Dict


WIND_MATRIX: Dict[BoatType, Dict[SkillLevel, Tuple[float, float]]] = {
    BoatType.DINGHY: {
        SkillLevel.PRINCIPIANTE: (6.0, 12.0),
        SkillLevel.INTERMEDIO: (8.0, 15.0),
        SkillLevel.AVANZADO: (10.0, 18.0)
    },
    BoatType.CATAMARAN_LIGERO: {
        SkillLevel.PRINCIPIANTE: (8.0, 14.0),
        SkillLevel.INTERMEDIO: (10.0, 18.0),
        SkillLevel.AVANZADO: (12.0, 22.0)
    },
    BoatType.VELERO_PEQUENO: {
        SkillLevel.PRINCIPIANTE: (8.0, 14.0),
        SkillLevel.INTERMEDIO: (10.0, 17.0),
        SkillLevel.AVANZADO: (12.0, 20.0)
    },
    BoatType.VELERO_MEDIO: {
        SkillLevel.PRINCIPIANTE: (10.0, 16.0),
        SkillLevel.INTERMEDIO: (11.0, 20.0),
        SkillLevel.AVANZADO: (12.0, 24.0)
    },
    BoatType.VELERO_GRANDE: {
        SkillLevel.PRINCIPIANTE: (10.0, 18.0),
        SkillLevel.INTERMEDIO: (12.0, 22.0),
        SkillLevel.AVANZADO: (14.0, 26.0)
    },
    BoatType.TABLAS: {
        SkillLevel.PRINCIPIANTE: (12.0, 20.0),
        SkillLevel.INTERMEDIO: (15.0, 25.0),
        SkillLevel.AVANZADO: (18.0, 30.0)
    }
}


def score_wind(wind_kn: float, boat_type: BoatType, skill: SkillLevel) -> Tuple[float, str]:
    """
    Calcula puntuación base por viento usando algoritmo actualizado.
    Base 60 puntos en óptimo con penalizaciones suaves por déficit.
    Retorna (puntos, razón)
    """
    optimal_range = WIND_MATRIX[boat_type][skill]
    min_optimal, max_optimal = optimal_range
    
    if min_optimal <= wind_kn <= max_optimal:
        score = 60.0  # Base para condiciones óptimas
        reason = f"Viento {wind_kn:.1f} kn en rango óptimo"
    else:
        if wind_kn < min_optimal:
            deficit = min_optimal - wind_kn
            # Ajuste suave según nuevo algoritmo
            if deficit <= 1:
                # Hasta -1 punto por nudo de déficit leve
                score = max(60.0 - 1.0 * deficit, 52.0)
            elif deficit <= 2:
                # Hasta -2 con caída a -2 puntos/nudo adicional
                score = max(60.0 - (1 + 2 * (deficit - 1)), 40.0)
            elif deficit <= 4:
                # Caída más pronunciada
                score = max(60.0 - (3 + 3 * (deficit - 2)), 30.0)
            else:
                # Déficit muy grande, caída fuerte
                score = max(60.0 - (9 + 4 * (deficit - 4)), 25.0)
            
            reason = f"Viento {wind_kn:.1f} kn (óptimo {min_optimal:.0f}-{max_optimal:.0f})"
        else:
            # Exceso se mantiene más severo que déficit
            excess = wind_kn - max_optimal
            score = max(60.0 - 3.0 * excess, 30.0)
            reason = f"Viento {wind_kn:.1f} kn (óptimo {min_optimal:.0f}-{max_optimal:.0f})"
    
    return score, reason


def score_gust_factor(wind_kn: float, gust_kn: float, skill: SkillLevel, in_optimal_range: bool = False) -> Tuple[float, str]:
    """
    Penaliza por factor de rachas con enfoque híbrido:
    - Vientos bajos: usa umbrales absolutos (evita penalizar rachas pequeñas)
    - Vientos óptimos/altos: usa ratio de rachas
    Retorna (penalización, flag opcional)
    """
    if wind_kn < 1.0:
        return 0.0, ""
    
    gust_weights = {
        SkillLevel.PRINCIPIANTE: 1.0,
        SkillLevel.INTERMEDIO: 0.7,
        SkillLevel.AVANZADO: 0.5
    }
    multiplier = gust_weights[skill]
    gust_delta = gust_kn - wind_kn
    
    # Para vientos fuera del rango óptimo (bajos): usar umbrales absolutos
    if not in_optimal_range:
        # Rachas pequeñas en viento bajo: sin penalización
        if gust_kn < 10.0 or gust_delta < 4.0:
            return 0.0, ""
        # Rachas moderadas
        elif gust_kn < 14.0 or gust_delta < 6.0:
            return -3.0 * multiplier, ""
        # Rachas irregulares
        elif gust_kn < 18.0 or gust_delta < 8.0:
            return -6.0 * multiplier, f"Rachas irregulares ({gust_kn:.1f} kn)"
        # Rachas fuertes (solo si realmente son fuertes)
        else:
            return -10.0 * multiplier, f"Rachas fuertes ({gust_kn:.1f} kn)"
    
    # Para vientos en rango óptimo: usar ratio pero más permisivo
    gust_factor = gust_kn / wind_kn
    
    if gust_factor <= 1.25:
        return 0.0, ""
    elif gust_factor <= 1.4:
        return -5.0 * multiplier, ""
    elif gust_factor <= 1.6:
        penalty = -10.0 * multiplier
        flag = f"Rachas irregulares ({gust_kn:.1f} kn)" if gust_kn >= 16.0 else ""
        return penalty, flag
    else:
        # Solo penalizar fuerte si las rachas son realmente peligrosas
        penalty = -20.0 * multiplier if gust_kn >= 22.0 else -15.0 * multiplier
        flag = f"Rachas fuertes ({gust_kn:.1f} kn)" if gust_kn >= 18.0 else f"Rachas irregulares ({gust_kn:.1f} kn)"
        return penalty, flag
