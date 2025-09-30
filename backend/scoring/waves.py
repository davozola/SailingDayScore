from backend.models import BoatType, SkillLevel
from typing import Tuple, Optional, Dict
import math


WAVE_MATRIX: Dict[BoatType, Dict[SkillLevel, Tuple[float, float, float]]] = {
    BoatType.DINGHY: {
        SkillLevel.PRINCIPIANTE: (0.4, 0.5, 0.6),
        SkillLevel.INTERMEDIO: (0.5, 0.7, 0.8),
        SkillLevel.AVANZADO: (0.6, 0.8, 1.0)
    },
    BoatType.CATAMARAN_LIGERO: {
        SkillLevel.PRINCIPIANTE: (0.5, 0.6, 0.8),
        SkillLevel.INTERMEDIO: (0.7, 1.0, 1.2),
        SkillLevel.AVANZADO: (0.9, 1.2, 1.5)
    },
    BoatType.VELERO_PEQUENO: {
        SkillLevel.PRINCIPIANTE: (0.6, 0.8, 1.0),
        SkillLevel.INTERMEDIO: (0.8, 1.3, 1.5),
        SkillLevel.AVANZADO: (1.0, 1.6, 2.0)
    },
    BoatType.VELERO_MEDIO: {
        SkillLevel.PRINCIPIANTE: (0.8, 1.2, 1.5),
        SkillLevel.INTERMEDIO: (1.0, 1.7, 2.0),
        SkillLevel.AVANZADO: (1.2, 2.0, 2.5)
    },
    BoatType.VELERO_GRANDE: {
        SkillLevel.PRINCIPIANTE: (1.0, 1.5, 2.0),
        SkillLevel.INTERMEDIO: (1.3, 2.2, 2.5),
        SkillLevel.AVANZADO: (1.5, 2.5, 3.0)
    },
    BoatType.TABLAS: {
        SkillLevel.PRINCIPIANTE: (0.5, 0.6, 0.8),
        SkillLevel.INTERMEDIO: (0.7, 1.0, 1.2),
        SkillLevel.AVANZADO: (0.9, 1.2, 1.5)
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
        # Bonus gradual para olas más pequeñas: 0.3m mejor que 0.7m
        # Máximo +8 puntos para olas muy pequeñas (0.2m), 0 puntos en el límite óptimo
        bonus = 8.0 * (1.0 - hs_m / optimal)
        return bonus, f"Ola {hs_m:.1f} m (favorable)"
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


def score_wave_period(tp_s: Optional[float], hs_m: Optional[float] = None) -> Tuple[float, str]:
    """
    Bonus/penalización por periodo de ola.
    Si hay mar de fondo con ola baja, bonus adicional.
    Retorna (ajuste, razón)
    """
    if tp_s is None:
        return 0.0, ""
    
    bonus = 0.0
    reason = ""
    
    # Escalar el bonus por la altura de ola para evitar que periodos buenos
    # hagan que olas altas puntúen mejor que olas bajas
    # Factor de escala: 1.0 para olas ≤0.4m, reduce más agresivamente hasta 0.4 en 1.5m
    scale_factor = 1.0
    if hs_m is not None:
        if hs_m <= 0.4:
            scale_factor = 1.0
        elif hs_m <= 1.5:
            # Reducción más pronunciada: de 1.0 a 0.4
            scale_factor = 1.0 - 0.6 * (hs_m - 0.4) / 1.1  # 1.0 → 0.4
        else:
            scale_factor = 0.4
    
    if tp_s >= 8.0:
        bonus = 10.0 * scale_factor
        reason = f"Tp {tp_s:.1f} s (mar de fondo suave, muy navegable)"
        # Bonus adicional si además la ola es baja
        if hs_m and hs_m <= 1.5:
            bonus += 5.0 * scale_factor
            reason = f"Tp {tp_s:.1f} s + ola {hs_m:.1f}m (condiciones ideales)"
    elif tp_s >= 7.0:
        bonus = 7.0 * scale_factor
        reason = f"Tp {tp_s:.1f} s (mar de fondo)"
    elif tp_s < 5.0:
        bonus = -6.0
        reason = f"Tp {tp_s:.1f} s (mar corto, incómodo)"
    
    return bonus, reason


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
