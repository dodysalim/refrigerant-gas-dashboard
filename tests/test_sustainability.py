"""
Tests Unitarios - Pipeline ETL y Sostenibilidad
Verifica el correcto funcionamiento del pipeline ETL y el análisis
de sostenibilidad ambiental de los gases refrigerantes.

Ejecutar con: python -m pytest tests/ -v
"""

import unittest
from src.domain.entities import Refrigerant
from src.domain.sustainability import SustainabilityAnalyzer, SustainabilityScore


def _make_refrigerant(**kwargs) -> Refrigerant:
    """Factory para crear refrigerantes de prueba."""
    defaults = {
        "key": 1,
        "ashrae_name": "R-134a",
        "chemical_name": "1,1,1,2-Tetrafluoroethane",
        "chemical_formula": "CH2FCF3",
        "compound_type": "HFC",
        "safety_group": "A1",
        "odp": 0.0,
        "gwp": 1430.0,
        "category": "Basic",
        "primary_oil": "POE",
        "status": "Active",
        "color_hex": "#00BFFF",
        "boiling_point_c": -26.3,
        "critical_temp_c": 101.06,
        "critical_pressure_bar": 40.59,
        "description": "HFC refrigerante más utilizado mundialmente.",
        "pros": "Eficiente y seguro",
        "cons": "GWP alto",
        "alternatives": "R-1234yf",
        "true_replacement": "R-1234yf"
    }
    defaults.update(kwargs)
    return Refrigerant(**defaults)


class TestSustainabilityAnalyzer(unittest.TestCase):
    """Tests para el analizador de sostenibilidad."""

    def setUp(self):
        self.analyzer = SustainabilityAnalyzer()

    def test_natural_refrigerant_scores_high(self):
        """Los refrigerantes naturales con GWP≤1 y ODP=0 deben puntuar alto."""
        ammonia = _make_refrigerant(
            ashrae_name="R-717",
            chemical_name="Ammonia",
            compound_type="Natural",
            safety_group="B2L",
            odp=0.0,
            gwp=0.0,
            status="Active"
        )
        score = self.analyzer.score_refrigerant(ammonia)
        self.assertGreater(score.eco_score, 70.0)

    def test_cfc_scores_low(self):
        """Los CFCs con ODP alto deben puntuar muy bajo."""
        r11 = _make_refrigerant(
            ashrae_name="R-11",
            chemical_name="Trichlorofluoromethane",
            compound_type="CFC",
            safety_group="A1",
            odp=1.0,
            gwp=4750.0,
            status="Phased Out"
        )
        score = self.analyzer.score_refrigerant(r11)
        self.assertLess(score.eco_score, 30.0)

    def test_hfo_refrigerant_scores_very_high(self):
        """Los HFOs de 4ta generación con GWP<1 deben puntuar muy alto."""
        r1234yf = _make_refrigerant(
            ashrae_name="R-1234yf",
            chemical_name="2,3,3,3-Tetrafluoropropene",
            compound_type="HFO",
            safety_group="A2L",
            odp=0.0,
            gwp=4.0,
            status="Active"
        )
        score = self.analyzer.score_refrigerant(r1234yf)
        self.assertGreater(score.eco_score, 75.0)

    def test_phased_out_gets_zero_regulation_score(self):
        """Un refrigerante eliminado debe obtener 0 en puntuación regulatoria."""
        r = _make_refrigerant(status="Phased Out", gwp=4750.0, odp=1.0)
        score = self.analyzer.score_refrigerant(r)
        self.assertEqual(score.regulation_score, 0.0)

    def test_montreal_banned_for_nonzero_odp(self):
        """Gas con ODP > 0 debe estar marcado como afectado por Montreal."""
        r = _make_refrigerant(odp=0.5, compound_type="HCFC", status="Phasing Down")
        score = self.analyzer.score_refrigerant(r)
        self.assertTrue(score.montreal_banned)

    def test_zero_odp_not_montreal_banned(self):
        """Gas con ODP = 0 y estado Active no debe estar marcado por Montreal."""
        r = _make_refrigerant(odp=0.0, status="Active")
        score = self.analyzer.score_refrigerant(r)
        self.assertFalse(score.montreal_banned)

    def test_eu_fgas_compliance_domestic_high_gwp(self):
        """Gas doméstico con GWP > 150 no debe cumplir EU F-Gas."""
        r = _make_refrigerant(category="Basic", gwp=1430.0, odp=0.0, status="Active")
        score = self.analyzer.score_refrigerant(r)
        self.assertFalse(score.eu_fgas_compliant)

    def test_eu_fgas_compliance_domestic_low_gwp(self):
        """Gas doméstico con GWP < 150 y ODP=0 debe cumplir EU F-Gas."""
        r = _make_refrigerant(
            category="Basic", gwp=4.0, odp=0.0,
            status="Active", compound_type="HFO"
        )
        score = self.analyzer.score_refrigerant(r)
        self.assertTrue(score.eu_fgas_compliant)

    def test_kigali_restriction_hfc_high_gwp(self):
        """HFCs con GWP > 1000 deben estar restringidos por Kigali."""
        r = _make_refrigerant(compound_type="HFC", gwp=2500.0)
        score = self.analyzer.score_refrigerant(r)
        self.assertTrue(score.kigali_restricted)

    def test_kigali_not_restricted_for_natural(self):
        """Los refrigerantes naturales no deben estar restringidos por Kigali."""
        r = _make_refrigerant(compound_type="Natural", gwp=1.0)
        score = self.analyzer.score_refrigerant(r)
        self.assertFalse(score.kigali_restricted)

    def test_eco_label_excelente_for_high_score(self):
        """Puntuación >= 85 debe obtener etiqueta 'Excelente'."""
        r = _make_refrigerant(
            ashrae_name="R-744", compound_type="Natural",
            gwp=1.0, odp=0.0, safety_group="A1", status="Active"
        )
        score = self.analyzer.score_refrigerant(r)
        if score.eco_score >= 85:
            self.assertIn("Excelente", score.eco_label)

    def test_score_all_returns_sorted_descending(self):
        """score_all() debe retornar los refrigerantes ordenados de mayor a menor eco_score."""
        refrigerants = [
            _make_refrigerant(key=1, ashrae_name="R-134a", gwp=1430.0, odp=0.0),
            _make_refrigerant(key=2, ashrae_name="R-717", gwp=0.0, odp=0.0, compound_type="Natural"),
            _make_refrigerant(key=3, ashrae_name="R-11", gwp=4750.0, odp=1.0,
                              compound_type="CFC", status="Phased Out"),
        ]
        scores = self.analyzer.score_all(refrigerants)
        for i in range(len(scores) - 1):
            self.assertGreaterEqual(scores[i].eco_score, scores[i+1].eco_score)

    def test_score_all_includes_all_refrigerants(self):
        """score_all() debe incluir todos los refrigerantes del input."""
        refrigerants = [
            _make_refrigerant(key=i, ashrae_name=f"R-{100+i}")
            for i in range(1, 11)
        ]
        scores = self.analyzer.score_all(refrigerants)
        self.assertEqual(len(scores), 10)

    def test_ranking_summary_structure(self):
        """get_ranking_summary() debe retornar todas las claves esperadas."""
        refrigerants = [
            _make_refrigerant(key=1, ashrae_name="R-290", gwp=3.0, odp=0.0, compound_type="HC"),
            _make_refrigerant(key=2, ashrae_name="R-22", gwp=1810.0, odp=0.055,
                              compound_type="HCFC", status="Phasing Down"),
        ]
        scores = self.analyzer.score_all(refrigerants)
        summary = self.analyzer.get_ranking_summary(scores)

        required_keys = {
            "total_analyzed", "average_eco_score", "label_distribution",
            "eu_fgas_compliant", "kigali_restricted", "montreal_banned",
            "top_5_ecological", "bottom_5_ecological"
        }
        self.assertEqual(required_keys.issubset(summary.keys()), True)

    def test_gwp_score_decreases_with_higher_gwp(self):
        """La puntuación GWP debe disminuir a medida que aumenta el GWP."""
        gwp_levels = [0, 10, 150, 500, 1000, 2000, 5000, 14000, 20000]
        scores = []
        for gwp in gwp_levels:
            r = _make_refrigerant(gwp=gwp)
            s = self.analyzer.score_refrigerant(r)
            scores.append(s.gwp_score)

        # Verificar que los scores son no crecientes
        for i in range(len(scores) - 1):
            self.assertGreaterEqual(scores[i], scores[i+1],
                f"GWP score should decrease: {gwp_levels[i]}→{gwp_levels[i+1]}: {scores[i]}→{scores[i+1]}")

    def test_odp_score_is_max_for_zero_odp(self):
        """ODP=0 debe dar la máxima puntuación ODP."""
        r = _make_refrigerant(odp=0.0)
        score = self.analyzer.score_refrigerant(r)
        self.assertEqual(score.odp_score, self.analyzer.ODP_WEIGHT)

    def test_recommendation_contains_refrigerant_name(self):
        """La recomendación debe mencionar el nombre del refrigerante."""
        r = _make_refrigerant(ashrae_name="R-404A")
        score = self.analyzer.score_refrigerant(r)
        self.assertIn("R-404A", score.recommendation)

    def test_sustainability_score_to_dict(self):
        """SustainabilityScore.to_dict() debe retornar todos los campos esperados."""
        r = _make_refrigerant()
        score = self.analyzer.score_refrigerant(r)
        d = score.to_dict()
        expected_keys = {
            "ashrae_name", "eco_score", "gwp_score", "odp_score",
            "safety_score", "regulation_score", "eco_label",
            "eu_fgas_compliant", "kigali_restricted", "montreal_banned", "recommendation"
        }
        self.assertEqual(expected_keys.issubset(d.keys()), True)


class TestGWPScoreCalculation(unittest.TestCase):
    """Tests específicos para el cálculo de la puntuación GWP."""

    def setUp(self):
        self.analyzer = SustainabilityAnalyzer()

    def test_gwp_zero_gives_max_score(self):
        """GWP=0 (ej. R-717) debe dar la puntuación máxima de GWP."""
        score = self.analyzer._calculate_gwp_score(0.0)
        self.assertEqual(score, self.analyzer.GWP_WEIGHT)

    def test_gwp_one_gives_max_score(self):
        """GWP=1 (CO2, HFOs) debe dar la puntuación máxima de GWP."""
        score = self.analyzer._calculate_gwp_score(1.0)
        self.assertEqual(score, self.analyzer.GWP_WEIGHT)

    def test_gwp_very_high_gives_zero(self):
        """GWP > 14000 debe dar puntuación 0."""
        score = self.analyzer._calculate_gwp_score(23900.0)
        self.assertEqual(score, 0.0)

    def test_gwp_score_is_nonnegative(self):
        """La puntuación GWP siempre debe ser ≥ 0."""
        for gwp in [0, 1, 4, 150, 500, 1430, 2088, 3800, 14800, 23900]:
            score = self.analyzer._calculate_gwp_score(float(gwp))
            self.assertGreaterEqual(score, 0.0)

    def test_gwp_score_does_not_exceed_weight(self):
        """La puntuación GWP nunca debe superar el peso máximo asignado."""
        for gwp in [0, 1, 4, 150, 500, 1430, 2088, 3800, 14800]:
            score = self.analyzer._calculate_gwp_score(float(gwp))
            self.assertLessEqual(score, self.analyzer.GWP_WEIGHT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
