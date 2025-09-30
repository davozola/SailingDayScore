from backend.models import BoatType, SkillLevel
from typing import Tuple, Optional, Dict
import math


WAVE_MATRIX: Dict[BoatType, Dict[SkillLevel, Tuple[float, float, float]]] = {
    BoatType.VELA_LIGERA: {
        SkillLevel.PRINCIPIANTE: (0.6, 1.0, 1.5),
        SkillLevel.INTERMEDIO: (0.8, 1.3, 2.0),
        SkillLevel.AVANZADO: (1.0, 1.8, 2.5)
    },
    BoatType.CRUISER_35: {
        SkillLevel.PRINCIPIANTE: (0.8, 1.5, 2.0),
        SkillLevel.INTERMEDIO: (1.0, 2.0, 2.5),
        SkillLevel.AVANZADO: (1.2, 2.5, 3.0)
    },
    BoatType.CRUISER_35_45: {
        SkillLevel.PRINCIPIANTE: (1.0, 1.8, 2.5),
        SkillLevel.INTERMEDIO: (1.2, 2.0, 3.0),
        SkillLevel.AVANZADO: (1.5, 2.8, 3.5)
    },
    BoatType.CATAMARAN: {
        SkillLevel.PRINCIPIANTE: (0.8, 1.5, 2.0),
        SkillLevel.INTERMEDIO: (1.0, 2.0, 2.5),
        SkillLevel.AVANZADO: (1.2, 2.5, 3.0)
    },
    BoatType.DINGHY: {
        SkillLevel.PRINCIPIANTE: (0.5, 0.8, 1.2),
        SkillLevel.INTERMEDIO: (0.7, 1.2, 1.8),
        SkillLevel.AVANZADO: (0.9, 1.5, 2.2)
    },
    BoatType.WINDSURF: {
        SkillLevel.PRINCIPIANTE: (0.5, 0.8, 1.2),
        SkillLevel.INTERMEDIO: (0.7, 1.2, 1.8),
        SkillLevel.AVANZADO: (0.9, 1.5, 2.2)
    }
}


def score_wave_height(hs_m: Optional[float], boat_type: BoatType, skill: SkillLevel, tp_s: Optional[float] = None) -> Tuple[float, str]:
    """
    Penaliza por altura significativa de ola, considerando el periodo.
    Retorna (penalización, razón)
    """
    if hs_m is None:
        return -8.0, "Sin datos de mar"
    
    optimal, moderate, limit = WAVE_MATRIX[boat_type][skill]
    
    # Si el periodo es largo (>=7s), es mar de fondo: más navegable que mar de viento
    period_factor = 1.0
    if tp_s and tp_s >= 7.0:
        period_factor = 0.6  # Reduce penalización en 40% para mar de fondo
    elif tp_s and tp_s >= 5.5:
        period_factor = 0.8  # Reduce penalización en 20% para periodos moderados
    
    if hs_m <= optimal:
        return 0.0, f"Ola {hs_m:.1f} m (favorable)"
    elif hs_m <= moderate:
        penalty = -25.0 * (hs_m - optimal) / (moderate - optimal) * period_factor
        label = "moderada, navegable" if tp_s and tp_s >= 7.0 else "moderada"
        return penalty, f"Ola {hs_m:.1f} m ({label})"
    elif hs_m <= limit:
        penalty = (-25.0 - 15.0 * (hs_m - moderate) / (limit - moderate)) * period_factor
        label = "alta, mar de fondo" if tp_s and tp_s >= 7.0 else "alta"
        return penalty, f"Ola {hs_m:.1f} m ({label})"
    else:
        return -40.0 * period_factor, f"Ola {hs_m:.1f} m (muy alta)"


def score_wave_period(tp_s: Optional[float]) -> Tuple[float, str]:
    """
    Bonus/penalización por periodo de ola.
    Retorna (ajuste, razón)
    """
    if tp_s is None:
        return 0.0, ""
    
    if tp_s >= 8.0:
        return 8.0, f"Tp {tp_s:.1f} s (mar de fondo suave, muy navegable)"
    elif tp_s >= 7.0:
        return 5.0, f"Tp {tp_s:.1f} s (mar de fondo)"
    elif tp_s < 5.0:
        return -6.0, f"Tp {tp_s:.1f} s (mar corto, incómodo)"
    else:
        return 0.0, ""


def score_wave_wind_direction(wave_dir: Optional[float], wind_dir: Optional[float]) -> Tuple[float, str]:
    """
    Ajuste por relación entre dirección de ola y viento.
    Retorna (ajuste, flag opcional)
    """
    if wave_dir is None or wind_dir is None:
        return 0.0, ""
    
    diff = abs(wave_dir - wind_dir)
    if diff > 180:
        diff = 360 - diff
    
    if diff < 40:
        return -4.0, "Mar de viento"
    elif diff > 140:
        return 3.0, "Mar de largo"
    else:
        return 0.0, ""
