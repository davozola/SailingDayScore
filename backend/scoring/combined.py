from backend.models import BoatType, SkillLevel, RawMetrics, WindowScore, Safety
from backend.scoring.wind import score_wind, score_gust_factor
from backend.scoring.waves import score_wave_height, score_wave_period, score_wave_wind_direction
from typing import List, Tuple


NO_GO_THRESHOLDS = {
    SkillLevel.PRINCIPIANTE: {"wind": 20.0, "gust": 28.0, "wave": 1.5},
    SkillLevel.INTERMEDIO: {"wind": 25.0, "gust": 35.0, "wave": 2.5},
    SkillLevel.AVANZADO: {"wind": 32.0, "gust": 40.0, "wave": 3.0}
}


def score_precipitation(precip_mm_h: float) -> Tuple[float, str]:
    """Penaliza por precipitación"""
    if precip_mm_h < 0.5:
        return 0.0, ""
    elif precip_mm_h <= 2.0:
        return -2.0, ""
    elif precip_mm_h <= 5.0:
        return -6.0, "Precipitación moderada"
    else:
        return -15.0, "Precipitación intensa"


def score_temperature(temp_c: float) -> Tuple[float, str]:
    """Penaliza por temperatura fuera de rango confortable"""
    if 10.0 <= temp_c <= 32.0:
        return 0.0, ""
    elif temp_c < 10.0:
        delta = 10.0 - temp_c
        return -0.8 * delta, f"Temperatura baja ({temp_c:.1f}°C)"
    else:
        delta = temp_c - 32.0
        return -0.8 * delta, f"Temperatura alta ({temp_c:.1f}°C)"


def check_no_go(metrics: RawMetrics, skill: SkillLevel) -> Tuple[bool, List[str]]:
    """Verifica si las condiciones son no_go según el nivel"""
    thresholds = NO_GO_THRESHOLDS[skill]
    reasons = []
    
    if metrics.wind_kn > thresholds["wind"]:
        reasons.append(f"Viento {metrics.wind_kn:.1f} kn supera límite ({thresholds['wind']:.0f} kn)")
    
    if metrics.gust_kn > thresholds["gust"]:
        reasons.append(f"Rachas {metrics.gust_kn:.1f} kn superan límite ({thresholds['gust']:.0f} kn)")
    
    if metrics.wave_hs_m and metrics.wave_hs_m > thresholds["wave"]:
        reasons.append(f"Ola {metrics.wave_hs_m:.1f} m supera límite ({thresholds['wave']:.1f} m)")
    
    return len(reasons) > 0, reasons


def calculate_score(metrics: RawMetrics, boat_type: BoatType, skill: SkillLevel) -> Tuple[int, str, List[str], List[str]]:
    """
    Calcula la puntuación completa para una ventana temporal.
    Retorna (score, label, reasons, flags)
    """
    total_score = 0.0
    reasons = []
    flags = []
    
    wind_score, wind_reason = score_wind(metrics.wind_kn, boat_type, skill)
    total_score += wind_score
    reasons.append(wind_reason)
    
    # Determinar si el viento está en rango óptimo para ajustar penalización de rachas
    from backend.scoring.wind import WIND_MATRIX
    optimal_range = WIND_MATRIX[boat_type][skill]
    in_optimal = optimal_range[0] <= metrics.wind_kn <= optimal_range[1]
    
    gust_penalty, gust_flag = score_gust_factor(metrics.wind_kn, metrics.gust_kn, skill, in_optimal)
    total_score += gust_penalty
    if gust_flag:
        flags.append(gust_flag)
    
    wave_penalty, wave_reason = score_wave_height(metrics.wave_hs_m, boat_type, skill, metrics.wave_tp_s)
    total_score += wave_penalty
    if wave_reason:
        reasons.append(wave_reason)
    
    period_adj, period_reason = score_wave_period(metrics.wave_tp_s, metrics.wave_hs_m)
    total_score += period_adj
    if period_reason:
        reasons.append(period_reason)
    
    dir_adj, dir_flag = score_wave_wind_direction(metrics.wave_dir_deg, metrics.wind_dir_deg)
    total_score += dir_adj
    if dir_flag:
        flags.append(dir_flag)
    
    precip_penalty, precip_flag = score_precipitation(metrics.precip_mm_h)
    total_score += precip_penalty
    if precip_flag:
        flags.append(precip_flag)
    
    if metrics.precip_mm_h > 2.0:
        flags.append("Posible visibilidad reducida")
    
    temp_penalty, temp_flag = score_temperature(metrics.temp_c)
    total_score += temp_penalty
    if temp_flag:
        flags.append(temp_flag)
    
    if metrics.wave_hs_m is None:
        flags.append("Sin datos de mar (estimación conservadora)")
    
    # Verificar si es no-go absoluto
    is_no_go, no_go_reasons = check_no_go(metrics, skill)
    
    # Si es no-go absoluto, score bajo y añadir razones a flags
    if is_no_go:
        score_clamped = max(0, min(30, int(round(total_score))))
        label = "No recomendable"
        # Añadir razones de no-go a flags
        for reason in no_go_reasons:
            flags.append(f"⚠️ NO-GO: {reason}")
    else:
        # Suelo suave para evitar castigo injusto por rachas con poco viento
        total_score = max(total_score, 35)
        
        # Clamp score entre 0 y 100
        score_clamped = max(0, min(100, int(round(total_score))))
        
        # Labels según nuevo algoritmo
        if score_clamped < 30:
            label = "No recomendable"
        elif score_clamped < 45:
            label = "A valorar con mucha cautela"
        elif score_clamped < 60:
            label = "Aceptable / depende de experiencia"
        elif score_clamped < 80:
            label = "Bueno"
        else:
            label = "Muy bueno"
    
    reasons = reasons[:3]
    
    return score_clamped, label, reasons, flags


def create_window_score(time: str, metrics: RawMetrics, boat_type: BoatType, skill: SkillLevel) -> WindowScore:
    """Crea un WindowScore completo"""
    score, label, reasons, flags = calculate_score(metrics, boat_type, skill)
    
    return WindowScore(
        time=time,
        score=score,
        label=label,
        reasons=reasons,
        flags=flags,
        raw=metrics
    )
