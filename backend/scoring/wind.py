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
    Calcula puntuación base por viento.
    Retorna (puntos, razón)
    """
    optimal_range = WIND_MATRIX[boat_type][skill]
    min_optimal, max_optimal = optimal_range
    
    if min_optimal <= wind_kn <= max_optimal:
        score = 75.0  # Condiciones óptimas
        reason = f"Viento {wind_kn:.1f} kn en rango óptimo"
    else:
        if wind_kn < min_optimal:
            delta = min_optimal - wind_kn
            # Penalización progresiva más suave para viento flojo
            # 0-3 kn bajo óptimo: -3 puntos/kn
            # 3-6 kn bajo óptimo: -4 puntos/kn adicional
            # 6+ kn bajo óptimo: -5 puntos/kn adicional
            if delta <= 3:
                penalty = delta * 3.0
            elif delta <= 6:
                penalty = (3 * 3.0) + ((delta - 3) * 4.0)
            else:
                penalty = (3 * 3.0) + (3 * 4.0) + ((delta - 6) * 5.0)
            
            score = max(75.0 - penalty, 20.0)
            reason = f"Viento {wind_kn:.1f} kn (flojo, óptimo {min_optimal:.0f}-{max_optimal:.0f} kn)"
        else:
            delta = wind_kn - max_optimal
            # Pendiente moderada para vientos fuertes (4 puntos por kn)
            score = max(75.0 - (delta * 4.0), 20.0)
            reason = f"Viento {wind_kn:.1f} kn (fuerte, óptimo {min_optimal:.0f}-{max_optimal:.0f} kn)"
    
    return score, reason


def score_gust_factor(wind_kn: float, gust_kn: float, skill: SkillLevel, in_optimal_range: bool = False) -> Tuple[float, str]:
    """
    Penaliza por factor de rachas según nivel de experiencia.
    Si el viento medio está en rango óptimo, las rachas penalizan menos.
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
    
    # Si el viento está en rango óptimo, reducir penalización de rachas más agresivamente
    # Esto permite que condiciones con viento óptimo no se penalicen tanto por rachas
    if in_optimal_range:
        multiplier *= 0.35  # Reducción de 65% (antes era 50%)
    
    # Umbrales más tolerantes para rachas cuando el viento medio es bueno
    threshold_adjust = 0.2 if in_optimal_range else 0.0
    
    if gust_factor <= 1.2 + threshold_adjust:
        return 0.0, ""
    elif gust_factor <= 1.35 + threshold_adjust:
        penalty = -5.0 * multiplier
        flag = f"Rachas moderadas +{percentage}% ({gust_kn:.1f} kn): mayor esfuerzo físico" if gust_kn >= 12.0 else ""
        return penalty, flag
    elif gust_factor <= 1.5 + threshold_adjust:
        penalty = -10.0 * multiplier
        flag = f"Rachas elevadas +{percentage}% ({gust_kn:.1f} kn): riesgo de orzadas y escoras bruscas" if gust_kn >= 15.0 else ""
        return penalty, flag
    elif gust_factor <= 1.7 + threshold_adjust:
        penalty = -15.0 * multiplier
        flag = f"Rachas muy fuertes +{percentage}% ({gust_kn:.1f} kn): velas difíciles de controlar" if gust_kn >= 18.0 and not in_optimal_range else ""
        return penalty, flag
    else:
        # Capear la penalización máxima en viento óptimo
        if in_optimal_range:
            penalty = min(-20.0 * multiplier, -8.0)  # Máximo -8 puntos en óptimo
            flag = f"Rachas variables +{percentage}% ({gust_kn:.1f} kn): mantenerse alerta" if gust_kn >= 18.0 else ""
        else:
            penalty = -20.0 * multiplier
            flag = f"Rachas extremas +{percentage}% ({gust_kn:.1f} kn): alto riesgo, control muy difícil" if gust_kn >= 22.0 else ""
        return penalty, flag
