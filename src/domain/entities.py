"""
Módulos de Dominio - Entidades
Define las estructuras de datos fundamentales para los gases refrigerantes y sus
puntos de presión-temperatura (P-T) aplicando principios OOP.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class Refrigerant:
    """
    Entidad de dominio que representa un Gas Refrigerante.
    """
    key: int
    ashrae_name: str
    chemical_name: str
    chemical_formula: str
    compound_type: str  # CFC, HCFC, HFC, HC, Natural, HFO, Blend
    safety_group: str   # A1, A2, A2L, A3, B1, B2L, B3, etc.
    odp: float          # Ozone Depletion Potential
    gwp: float          # Global Warming Potential
    category: str       # Basic, Intermediate, Industrial
    primary_oil: str    # Mineral, POE, PAG, AB, None
    status: str         # Active, Phased Out, Phasing Down
    color_hex: str      # Código hexadecimal de color representativo
    boiling_point_c: float
    critical_temp_c: float
    critical_pressure_bar: float
    description: str
    pros: str
    cons: str
    alternatives: str
    true_replacement: str

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la entidad a un diccionario plano."""
        return {
            "refrigerant_key": self.key,
            "ashrae_name": self.ashrae_name,
            "chemical_name": self.chemical_name,
            "chemical_formula": self.chemical_formula,
            "compound_type": self.compound_type,
            "safety_group": self.safety_group,
            "odp": self.odp,
            "gwp": self.gwp,
            "category": self.category,
            "primary_oil": self.primary_oil,
            "status": self.status,
            "color_hex": self.color_hex,
            "boiling_point_c": self.boiling_point_c,
            "critical_temp_c": self.critical_temp_c,
            "critical_pressure_bar": self.critical_pressure_bar,
            "description": self.description,
            "pros": self.pros,
            "cons": self.cons,
            "alternatives": self.alternatives,
            "true_replacement": self.true_replacement
        }

@dataclass
class TemperatureDimension:
    """
    Entidad que representa la dimensión de Temperatura.
    """
    key: int
    temp_c: float
    temp_f: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "temperature_key": self.key,
            "temperature_c": self.temp_c,
            "temperature_f": self.temp_f
        }

@dataclass
class StateDimension:
    """
    Entidad que representa la dimensión de Fase/Estado.
    """
    key: int
    state_name: str  # Saturated Liquid (Bubble Point), Saturated Vapor (Dew Point)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_key": self.key,
            "state_name": self.state_name
        }

@dataclass
class SaturatedPressureFact:
    """
    Entidad que representa un registro en la tabla de hechos P-T.
    """
    refrigerant_key: int
    temperature_key: int
    state_key: int
    pressure_bar: float
    pressure_psi: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "refrigerant_key": self.refrigerant_key,
            "temperature_key": self.temperature_key,
            "state_key": self.state_key,
            "pressure_bar": round(self.pressure_bar, 4),
            "pressure_psi": round(self.pressure_psi, 2)
        }
