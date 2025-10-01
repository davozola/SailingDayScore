import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.models import BoatType, SkillLevel, RawMetrics
from backend.scoring.wind import score_wind, score_gust_factor
from backend.scoring.waves import score_wave_height, score_wave_period, score_wave_wind_direction
from backend.scoring.combined import calculate_score, check_no_go


class TestWindScoring:
    def test_optimal_wind(self):
        score, reason = score_wind(15.0, BoatType.VELERO_MEDIO, SkillLevel.INTERMEDIO)
        assert score == 60.0  # Nueva base 60 puntos
        assert "óptimo" in reason
    
    def test_low_wind(self):
        score, reason = score_wind(5.0, BoatType.VELERO_MEDIO, SkillLevel.INTERMEDIO)
        assert score < 60.0
        assert "óptimo" in reason  # Cambio de texto
    
    def test_high_wind(self):
        score, reason = score_wind(30.0, BoatType.VELERO_MEDIO, SkillLevel.INTERMEDIO)
        assert score < 60.0
        assert "óptimo" in reason  # Cambio de texto
    
    def test_gust_factor_low(self):
        # Viento con rachas bajas (< 10 kn): sin penalización
        penalty, flag = score_gust_factor(8.0, 9.5, SkillLevel.INTERMEDIO)
        assert penalty == 0.0  # gust_kn < 10
        assert flag == ""
    
    def test_gust_factor_moderate(self):
        # Viento moderado con rachas >= 10 kn
        penalty, flag = score_gust_factor(10.0, 13.0, SkillLevel.INTERMEDIO)
        # gust_kn >= 10, gf=1.3, pen_rel=-3, pen_abs=-1.8, w=0.33, pen_raw=-1.6, pen=-1.12
        assert penalty < 0 and penalty >= -2.0
        assert flag == ""
    
    def test_gust_factor_high(self):
        # Viento alto con rachas >= 10 kn pero gf < 2.0
        penalty, flag = score_gust_factor(15.0, 21.75, SkillLevel.INTERMEDIO)
        # gust_kn >= 10, gf=1.45, pen_rel=-6, pen_abs=-4.05, w=0.75, pen_raw=-7.5, pen=-5.25
        assert penalty < -4.0
        assert flag == ""  # gf < 2.0, no flag
    
    def test_gust_factor_extreme(self):
        # Caso MUY justificado: viento alto (>15 kn) Y factor >= 2.0
        penalty, flag = score_gust_factor(16.0, 32.0, SkillLevel.INTERMEDIO)
        # wind > 15 y gf = 2.0 → flag "Rachas fuertes"
        assert penalty < -5.0
        assert "Rachas fuertes" in flag
    
    def test_gust_factor_low_wind(self):
        # Viento bajo con rachas < 10 kn: sin penalización
        penalty, flag = score_gust_factor(2.5, 4.5, SkillLevel.INTERMEDIO)
        assert penalty == 0.0  # gust_kn < 10
        assert flag == ""


class TestWaveScoring:
    def test_optimal_wave(self):
        penalty, reason = score_wave_height(1.0, BoatType.VELERO_MEDIO, SkillLevel.INTERMEDIO)
        assert penalty == 0.0
        assert "favorable" in reason
    
    def test_moderate_wave(self):
        penalty, reason = score_wave_height(1.8, BoatType.VELERO_MEDIO, SkillLevel.INTERMEDIO)
        assert penalty < 0
        assert "moderada" in reason or "elevada" in reason  # Texto actualizado
    
    def test_high_wave(self):
        penalty, reason = score_wave_height(2.5, BoatType.VELERO_MEDIO, SkillLevel.INTERMEDIO)
        assert penalty < -20
        assert "elevada" in reason  # Texto actualizado
    
    def test_no_wave_data(self):
        penalty, reason = score_wave_height(None, BoatType.VELERO_MEDIO, SkillLevel.INTERMEDIO)
        assert penalty == -8.0
        assert "Sin datos" in reason
    
    def test_good_wave_period(self):
        bonus, reason = score_wave_period(8.0)
        assert bonus == 5.0  # Nuevo algoritmo: +5 puntos
        assert "fondo" in reason
    
    def test_short_wave_period(self):
        penalty, reason = score_wave_period(4.0)
        assert penalty == -5.0  # Nuevo algoritmo: -5 por defecto
        assert "corto" in reason
    
    def test_wave_wind_direction_aligned(self):
        penalty, flag = score_wave_wind_direction(90.0, 100.0)
        assert penalty == -4.0
        assert "viento" in flag
    
    def test_wave_wind_direction_opposite(self):
        bonus, flag = score_wave_wind_direction(90.0, 270.0)
        assert bonus == 3.0
        assert "largo" in flag


class TestCombinedScoring:
    def test_perfect_conditions(self):
        metrics = RawMetrics(
            wind_kn=15.0,
            gust_kn=17.0,
            wave_hs_m=1.0,
            wave_tp_s=8.0,
            wave_dir_deg=180.0,
            wind_dir_deg=10.0,
            precip_mm_h=0.0,
            temp_c=22.0
        )
        score, label, reasons, flags = calculate_score(
            metrics, BoatType.VELERO_MEDIO, SkillLevel.INTERMEDIO
        )
        assert 60 <= score <= 100
        assert label in ["Bueno", "Muy bueno", "Excelente"]
    
    def test_bad_conditions(self):
        metrics = RawMetrics(
            wind_kn=35.0,
            gust_kn=45.0,
            wave_hs_m=3.5,
            wave_tp_s=4.0,
            wave_dir_deg=90.0,
            wind_dir_deg=100.0,
            precip_mm_h=8.0,
            temp_c=5.0
        )
        score, label, reasons, flags = calculate_score(
            metrics, BoatType.VELERO_MEDIO, SkillLevel.INTERMEDIO
        )
        assert score < 50
        assert label in ["No recomendable", "A valorar", "Aceptable"]
    
    def test_score_normalization(self):
        metrics = RawMetrics(
            wind_kn=50.0,
            gust_kn=70.0,
            wave_hs_m=5.0,
            wave_tp_s=3.0,
            wave_dir_deg=90.0,
            wind_dir_deg=100.0,
            precip_mm_h=15.0,
            temp_c=0.0
        )
        score, label, reasons, flags = calculate_score(
            metrics, BoatType.DINGHY, SkillLevel.PRINCIPIANTE
        )
        assert 0 <= score <= 100
    
    def test_no_go_principiante_wind(self):
        metrics = RawMetrics(
            wind_kn=25.0,
            gust_kn=30.0,
            wave_hs_m=0.8,
            wave_tp_s=7.0,
            wave_dir_deg=None,
            wind_dir_deg=None,
            precip_mm_h=0.0,
            temp_c=20.0
        )
        no_go, reasons = check_no_go(metrics, SkillLevel.PRINCIPIANTE)
        assert no_go == True
        assert len(reasons) > 0
    
    def test_no_go_principiante_gust(self):
        metrics = RawMetrics(
            wind_kn=15.0,
            gust_kn=32.0,
            wave_hs_m=0.8,
            wave_tp_s=7.0,
            wave_dir_deg=None,
            wind_dir_deg=None,
            precip_mm_h=0.0,
            temp_c=20.0
        )
        no_go, reasons = check_no_go(metrics, SkillLevel.PRINCIPIANTE)
        assert no_go == True
    
    def test_no_go_principiante_wave(self):
        metrics = RawMetrics(
            wind_kn=12.0,
            gust_kn=14.0,
            wave_hs_m=2.0,
            wave_tp_s=7.0,
            wave_dir_deg=None,
            wind_dir_deg=None,
            precip_mm_h=0.0,
            temp_c=20.0
        )
        no_go, reasons = check_no_go(metrics, SkillLevel.PRINCIPIANTE)
        assert no_go == True
    
    def test_safe_conditions_intermedio(self):
        metrics = RawMetrics(
            wind_kn=18.0,
            gust_kn=22.0,
            wave_hs_m=1.5,
            wave_tp_s=7.0,
            wave_dir_deg=None,
            wind_dir_deg=None,
            precip_mm_h=0.0,
            temp_c=20.0
        )
        no_go, reasons = check_no_go(metrics, SkillLevel.INTERMEDIO)
        assert no_go == False
    
    def test_safe_conditions_avanzado(self):
        metrics = RawMetrics(
            wind_kn=30.0,
            gust_kn=38.0,
            wave_hs_m=2.8,
            wave_tp_s=7.0,
            wave_dir_deg=None,
            wind_dir_deg=None,
            precip_mm_h=0.0,
            temp_c=20.0
        )
        no_go, reasons = check_no_go(metrics, SkillLevel.AVANZADO)
        assert no_go == False
