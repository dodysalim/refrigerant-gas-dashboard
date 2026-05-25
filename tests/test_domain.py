"""
Tests Unitarios - Dominio: Entidades y Validadores
Verifica el comportamiento correcto de las entidades de dominio y
los validadores de negocio para gases refrigerantes.

Ejecutar con: python -m pytest tests/ -v
"""

import unittest
from src.domain.entities import Refrigerant, TemperatureDimension, StateDimension, SaturatedPressureFact
from src.domain.validators import (
    RefrigerantValidator,
    SaturatedPressureFactValidator,
    DatasetValidator,
    ValidationResult
)


def _make_refrigerant(**kwargs) -> Refrigerant:
    """Factory para crear un refrigerante de prueba con valores por defecto válidos."""
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
        "description": "El refrigerante HFC más utilizado globalmente para refrigeración doméstica.",
        "pros": "Excelente eficiencia, sin ODP, seguro.",
        "cons": "GWP=1430, sujeto a regulación Kigali.",
        "alternatives": "R-1234yf, R-600a",
        "true_replacement": "R-1234yf"
    }
    defaults.update(kwargs)
    return Refrigerant(**defaults)


class TestRefrigerantEntity(unittest.TestCase):
    """Tests para la entidad Refrigerant."""

    def test_to_dict_returns_all_fields(self):
        """to_dict() debe retornar todos los campos definidos en la entidad."""
        r = _make_refrigerant()
        d = r.to_dict()
        expected_keys = {
            "refrigerant_key", "ashrae_name", "chemical_name", "chemical_formula",
            "compound_type", "safety_group", "odp", "gwp", "category", "primary_oil",
            "status", "color_hex", "boiling_point_c", "critical_temp_c",
            "critical_pressure_bar", "description", "pros", "cons",
            "alternatives", "true_replacement"
        }
        self.assertEqual(set(d.keys()), expected_keys)

    def test_to_dict_values_match_fields(self):
        """to_dict() debe retornar los valores correctos de cada campo."""
        r = _make_refrigerant(ashrae_name="R-717", gwp=0.0, odp=0.0)
        d = r.to_dict()
        self.assertEqual(d["ashrae_name"], "R-717")
        self.assertEqual(d["gwp"], 0.0)
        self.assertEqual(d["odp"], 0.0)

    def test_refrigerant_key_is_integer(self):
        """El key de la entidad debe ser un entero positivo."""
        r = _make_refrigerant(key=42)
        self.assertIsInstance(r.key, int)
        self.assertGreater(r.key, 0)


class TestTemperatureDimension(unittest.TestCase):
    """Tests para la entidad TemperatureDimension."""

    def test_celsius_to_fahrenheit_conversion(self):
        """La temperatura en Fahrenheit debe corresponder a la conversión de Celsius."""
        temp_c = 0.0
        expected_f = 32.0
        td = TemperatureDimension(key=1, temp_c=temp_c, temp_f=expected_f)
        self.assertAlmostEqual(td.temp_f, (td.temp_c * 9 / 5) + 32, places=2)

    def test_to_dict_structure(self):
        """to_dict() debe retornar la estructura correcta."""
        td = TemperatureDimension(key=5, temp_c=25.0, temp_f=77.0)
        d = td.to_dict()
        self.assertIn("temperature_key", d)
        self.assertIn("temperature_c", d)
        self.assertIn("temperature_f", d)
        self.assertEqual(d["temperature_key"], 5)


class TestSaturatedPressureFact(unittest.TestCase):
    """Tests para la entidad SaturatedPressureFact."""

    def test_to_dict_rounds_values(self):
        """to_dict() debe redondear pressure_bar a 4 decimales y pressure_psi a 2."""
        fact = SaturatedPressureFact(
            refrigerant_key=1,
            temperature_key=1,
            state_key=1,
            pressure_bar=3.14159265,
            pressure_psi=45.566789
        )
        d = fact.to_dict()
        self.assertEqual(d["pressure_bar"], 3.1416)
        self.assertEqual(d["pressure_psi"], 45.57)


class TestRefrigerantValidator(unittest.TestCase):
    """Tests para el validador de la entidad Refrigerant."""

    def setUp(self):
        self.validator = RefrigerantValidator()

    def test_valid_refrigerant_passes(self):
        """Un refrigerante con todos los campos válidos debe pasar la validación."""
        r = _make_refrigerant()
        result = self.validator.validate(r)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_invalid_compound_type_fails(self):
        """Un tipo de compuesto desconocido debe generar error."""
        r = _make_refrigerant(compound_type="INVALID_TYPE")
        result = self.validator.validate(r)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("compound_type" in e.lower() or "tipo" in e.lower() for e in result.errors))

    def test_invalid_safety_group_fails(self):
        """Un grupo de seguridad desconocido debe generar error."""
        r = _make_refrigerant(safety_group="C1")
        result = self.validator.validate(r)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("safety_group" in e.lower() or "seguridad" in e.lower() for e in result.errors))

    def test_negative_gwp_fails(self):
        """GWP negativo debe generar error de validación."""
        r = _make_refrigerant(gwp=-100.0)
        result = self.validator.validate(r)
        self.assertFalse(result.is_valid)

    def test_gwp_exceeding_maximum_fails(self):
        """GWP mayor al máximo físico plausible debe generar error."""
        r = _make_refrigerant(gwp=99999.0)
        result = self.validator.validate(r)
        self.assertFalse(result.is_valid)

    def test_negative_odp_fails(self):
        """ODP negativo debe generar error de validación."""
        r = _make_refrigerant(odp=-0.5)
        result = self.validator.validate(r)
        self.assertFalse(result.is_valid)

    def test_critical_temp_below_boiling_fails(self):
        """Temperatura crítica menor al punto de ebullición debe generar error."""
        r = _make_refrigerant(boiling_point_c=-26.3, critical_temp_c=-50.0)
        result = self.validator.validate(r)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("crítica" in e or "critical" in e.lower() for e in result.errors))

    def test_invalid_hex_color_fails(self):
        """Un código de color hexadecimal inválido debe generar error."""
        r = _make_refrigerant(color_hex="azul")
        result = self.validator.validate(r)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("color" in e.lower() or "hex" in e.lower() for e in result.errors))

    def test_valid_hex_color_passes(self):
        """Colores hexadecimales válidos deben pasar la validación."""
        for color in ["#FFFFFF", "#000000", "#FF5733", "#00bfff"]:
            r = _make_refrigerant(color_hex=color)
            result = self.validator.validate(r)
            # No debe haber error de color
            color_errors = [e for e in result.errors if "color" in e.lower() or "hex" in e.lower()]
            self.assertEqual(len(color_errors), 0, f"Color {color} should be valid")

    def test_high_gwp_active_generates_warning(self):
        """GWP alto en refrigerante activo debe generar advertencia."""
        r = _make_refrigerant(gwp=5000.0, status="Active")
        result = self.validator.validate(r)
        self.assertTrue(len(result.warnings) > 0)

    def test_empty_ashrae_name_fails(self):
        """Nombre ASHRAE vacío debe generar error."""
        r = _make_refrigerant(ashrae_name="")
        result = self.validator.validate(r)
        self.assertFalse(result.is_valid)

    def test_invalid_status_fails(self):
        """Estado no reconocido debe generar error."""
        r = _make_refrigerant(status="Unknown")
        result = self.validator.validate(r)
        self.assertFalse(result.is_valid)

    def test_all_valid_statuses_pass(self):
        """Todos los estados válidos deben pasar la validación."""
        for status in ["Active", "Phased Out", "Phasing Down", "Emerging"]:
            r = _make_refrigerant(status=status)
            result = self.validator.validate(r)
            status_errors = [e for e in result.errors if "status" in e.lower() or "estado" in e.lower()]
            self.assertEqual(len(status_errors), 0, f"Status '{status}' should be valid")

    def test_all_valid_compound_types_pass(self):
        """Todos los tipos de compuesto válidos deben pasar la validación."""
        for ct in ["CFC", "HCFC", "HFC", "HC", "Natural", "HFO", "Blend"]:
            r = _make_refrigerant(compound_type=ct)
            result = self.validator.validate(r)
            type_errors = [e for e in result.errors if "compound_type" in e.lower() or "tipo" in e.lower()]
            self.assertEqual(len(type_errors), 0, f"Compound type '{ct}' should be valid")


class TestSaturatedPressureFactValidator(unittest.TestCase):
    """Tests para el validador de hechos de presión-temperatura."""

    def setUp(self):
        self.validator = SaturatedPressureFactValidator()
        self.ref_key_range = range(1, 56)  # Simula 55 refrigerantes

    def _make_fact(**kwargs) -> SaturatedPressureFact:
        defaults = {
            "refrigerant_key": 1,
            "temperature_key": 5,
            "state_key": 1,
            "pressure_bar": 5.0,
            "pressure_psi": 72.52
        }
        defaults.update(kwargs)
        return SaturatedPressureFact(**defaults)

    def test_valid_fact_passes(self):
        """Un hecho P-T con valores válidos debe pasar la validación."""
        fact = SaturatedPressureFact(
            refrigerant_key=1, temperature_key=5, state_key=1,
            pressure_bar=5.0, pressure_psi=72.52
        )
        result = self.validator.validate(fact, self.ref_key_range)
        self.assertTrue(result.is_valid)

    def test_invalid_refrigerant_key_fails(self):
        """Una clave de refrigerante fuera de rango debe generar error."""
        fact = SaturatedPressureFact(
            refrigerant_key=9999, temperature_key=5, state_key=1,
            pressure_bar=5.0, pressure_psi=72.52
        )
        result = self.validator.validate(fact, self.ref_key_range)
        self.assertFalse(result.is_valid)

    def test_invalid_state_key_fails(self):
        """Una clave de estado diferente a 1 o 2 debe generar error."""
        fact = SaturatedPressureFact(
            refrigerant_key=1, temperature_key=5, state_key=5,
            pressure_bar=5.0, pressure_psi=72.52
        )
        result = self.validator.validate(fact, self.ref_key_range)
        self.assertFalse(result.is_valid)

    def test_negative_pressure_fails(self):
        """Presión negativa debe generar error de validación."""
        fact = SaturatedPressureFact(
            refrigerant_key=1, temperature_key=5, state_key=1,
            pressure_bar=-1.0, pressure_psi=-14.5
        )
        result = self.validator.validate(fact, self.ref_key_range)
        self.assertFalse(result.is_valid)


class TestDatasetValidator(unittest.TestCase):
    """Tests de integración para el validador de dataset completo."""

    def setUp(self):
        self.validator = DatasetValidator()

    def test_validate_all_valid_refrigerants(self):
        """Un conjunto de refrigerantes válidos debe tener 100% de validez."""
        refrigerants = [
            _make_refrigerant(key=i, ashrae_name=f"R-{100+i}")
            for i in range(1, 6)
        ]
        valid, invalid, issues = self.validator.validate_refrigerants(refrigerants)
        self.assertEqual(invalid, 0)
        self.assertEqual(valid, 5)

    def test_detect_duplicate_names(self):
        """Nombres duplicados en el dataset deben ser detectados."""
        r1 = _make_refrigerant(key=1, ashrae_name="R-134a")
        r2 = _make_refrigerant(key=2, ashrae_name="R-134a")  # Duplicado
        _, invalid, issues = self.validator.validate_refrigerants([r1, r2])
        self.assertGreater(invalid, 0)
        self.assertTrue(any("duplicado" in i.lower() or "duplicate" in i.lower() for i in issues))

    def test_mixed_valid_invalid_dataset(self):
        """Un dataset mixto debe detectar correctamente los inválidos."""
        r_valid = _make_refrigerant(key=1, ashrae_name="R-290")
        r_invalid = _make_refrigerant(key=2, ashrae_name="R-717", compound_type="INVALID")
        valid, invalid, _ = self.validator.validate_refrigerants([r_valid, r_invalid])
        self.assertEqual(valid, 1)
        self.assertEqual(invalid, 1)


class TestValidationResult(unittest.TestCase):
    """Tests para la clase ValidationResult."""

    def test_result_with_no_errors_is_valid(self):
        """Un ValidationResult sin errores debe ser válido."""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        self.assertTrue(result.is_valid)

    def test_result_repr_shows_valid_status(self):
        """El repr de un resultado válido debe mostrar '✅ VÁLIDO'."""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        self.assertIn("VÁLIDO", repr(result))

    def test_result_repr_shows_invalid_status(self):
        """El repr de un resultado inválido debe mostrar '❌ INVÁLIDO'."""
        result = ValidationResult(is_valid=False, errors=["Error test"], warnings=[])
        self.assertIn("INVÁLIDO", repr(result))

    def test_result_with_errors_is_invalid(self):
        """Un ValidationResult con errores debe ser inválido."""
        result = ValidationResult(is_valid=False, errors=["Error 1"], warnings=[])
        self.assertFalse(result.is_valid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
