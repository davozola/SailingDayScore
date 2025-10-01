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
    Penaliza por altura significativa de ola usando esquema piecewise (ok/soft_bad/hard_nogo).
    Retorna (penalización, razón)
    """
    if hs_m is None:
        return -8.0, "Sin datos de mar"
    
    ok, soft_bad, hard_nogo = WAVE_MATRIX[boat_type][skill]
    
    if hs_m <= ok:
        # Sin penalización en zona OK
        return 0.0, f"Ola {hs_m:.1f} m favorable"
    elif hs_m <= soft_bad:
        # Zona amarilla: hasta -15 puntos
        t = (hs_m - ok) / (soft_bad - ok)
        hs_pen = -round(t * 15)
        return float(hs_pen), f"Ola {hs_m:.1f} m moderada"
    else:
        # Zona roja: -15 a -25 según cercanía a hard_nogo
        t = min(1.0, (hs_m - soft_bad) / (hard_nogo - soft_bad))
        hs_pen = -(15 + round(t * 10))
        return float(hs_pen), f"Ola {hs_m:.1f} m elevada"


def score_wave_period(tp_s: Optional[float], hs_m: Optional[float] = None) -> Tuple[float, str]:
    """
    Ajuste por periodo de ola condicionado por Hs según nuevo algoritmo.
    Tp >= 7s: +5 puntos, Tp < 5s: penalización condicionada por Hs
    Retorna (ajuste, razón)
    """
    if tp_s is None:
        return 0.0, ""
    
    if tp_s >= 7.0:
        # Mar de fondo
        return 5.0, f"Tp {tp_s:.1f} s (mar de fondo)"
    elif tp_s < 5.0:
        # Mar corto, penalización condicionada por ola
        if hs_m is not None:
            if hs_m <= 0.5:
                return -3.0, f"Tp {tp_s:.1f} s (mar corto)"
            elif hs_m <= 0.8:
                return -5.0, f"Tp {tp_s:.1f} s (mar corto)"
            else:
                return -8.0, f"Tp {tp_s:.1f} s (mar corto)"
        else:
            return -5.0, f"Tp {tp_s:.1f} s (mar corto)"
    else:
        # Tp entre 5 y 7 segundos
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
