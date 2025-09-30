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
        score, reason = score_wind(12.0, BoatType.CRUISER_35_45, SkillLevel.INTERMEDIO)
        assert score == 60.0
        assert "óptimo" in reason
    
    def test_low_wind(self):
        score, reason = score_wind(5.0, BoatType.CRUISER_35_45, SkillLevel.INTERMEDIO)
        assert score < 60.0
        assert "flojo" in reason
    
    def test_high_wind(self):
        score, reason = score_wind(30.0, BoatType.CRUISER_35_45, SkillLevel.INTERMEDIO)
        assert score < 60.0
        assert "fuerte" in reason
    
    def test_gust_factor_low(self):
        penalty, flag = score_gust_factor(10.0, 11.0)
        assert penalty == 0.0
        assert flag == ""
    
    def test_gust_factor_moderate(self):
        penalty, flag = score_gust_factor(10.0, 13.0)
        assert penalty == -5.0
        assert "moderadas" in flag
    
    def test_gust_factor_high(self):
        penalty, flag = score_gust_factor(10.0, 14.5)
        assert penalty == -10.0
        assert "elevadas" in flag
    
    def test_gust_factor_extreme(self):
        penalty, flag = score_gust_factor(10.0, 16.0)
        assert penalty == -20.0
        assert "muy fuertes" in flag


class TestWaveScoring:
    def test_optimal_wave(self):
        penalty, reason = score_wave_height(0.8, BoatType.CRUISER_35_45, SkillLevel.INTERMEDIO)
        assert penalty == 0.0
        assert "favorable" in reason
    
    def test_moderate_wave(self):
        penalty, reason = score_wave_height(1.5, BoatType.CRUISER_35_45, SkillLevel.INTERMEDIO)
        assert penalty < 0
        assert "moderada" in reason or "alta" in reason
    
    def test_high_wave(self):
        penalty, reason = score_wave_height(3.5, BoatType.CRUISER_35_45, SkillLevel.INTERMEDIO)
        assert penalty < -30
        assert "muy alta" in reason
    
    def test_no_wave_data(self):
        penalty, reason = score_wave_height(None, BoatType.CRUISER_35_45, SkillLevel.INTERMEDIO)
        assert penalty == -8.0
        assert "Sin datos" in reason
    
    def test_good_wave_period(self):
        bonus, reason = score_wave_period(8.0)
        assert bonus == 5.0
        assert "fondo" in reason
    
    def test_short_wave_period(self):
        penalty, reason = score_wave_period(4.0)
        assert penalty == -6.0
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
            wind_kn=12.0,
            gust_kn=13.0,
            wave_hs_m=0.8,
            wave_tp_s=8.0,
            wave_dir_deg=180.0,
            wind_dir_deg=10.0,
            precip_mm_h=0.0,
            temp_c=22.0
        )
        score, label, reasons, flags = calculate_score(
            metrics, BoatType.CRUISER_35_45, SkillLevel.INTERMEDIO
        )
        assert 60 <= score <= 100
        assert label in ["Bueno", "Muy bueno"]
    
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
            metrics, BoatType.CRUISER_35_45, SkillLevel.INTERMEDIO
        )
        assert score < 40
        assert label in ["No recomendable", "Regular / con cautela"]
    
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
            metrics, BoatType.VELA_LIGERA, SkillLevel.PRINCIPIANTE
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
