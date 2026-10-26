"""Motor termodinámico: curvas de saturación presión-temperatura (P-T).

Las constantes por tipo de compuesto y el *glide* de las mezclas zeotrópicas están en
tablas: agregar un refrigerante especial no requiere modificar la lógica de cálculo.
"""
import math

from src.domain.entities import Refrigerant

ATM_BAR = 1.01325
MIN_PRESSURE_BAR = 0.005
BAR_TO_PSI = 14.5038

# Factor de Trouton (ΔH_vap / R·T_b) por refrigerante específico y por familia
TROUTON_BY_REFRIGERANT = {"R-717": 12.8, "R-744": 9.2}   # amoníaco (muy polar), CO2
TROUTON_NATURAL_DEFAULT = 10.6
TROUTON_BY_FAMILY = (("HFO", 10.2), ("HCFC", 10.8), ("CFC", 10.9))   # orden importa: HCFC antes que CFC
TROUTON_DEFAULT = 10.5                                                # HFC y mezclas

# Deslizamiento de temperatura (°C) de mezclas zeotrópicas
GLIDE_BY_REFRIGERANT = {"R-407C": 5.0, "R-407A": 4.5, "R-407F": 4.8, "R-448A": 4.7, "R-449A": 4.6, "R-455A": 12.0}
GLIDE_SERIES_400_DEFAULT = 2.0


def trouton_factor(refrigerant: Refrigerant) -> float:
    if refrigerant.compound_type == "Natural":
        return TROUTON_BY_REFRIGERANT.get(refrigerant.ashrae_name, TROUTON_NATURAL_DEFAULT)
    for family, factor in TROUTON_BY_FAMILY:
        if family in refrigerant.compound_type:
            return factor
    return TROUTON_DEFAULT


def glide(refrigerant: Refrigerant) -> float:
    if refrigerant.ashrae_name in GLIDE_BY_REFRIGERANT:
        return GLIDE_BY_REFRIGERANT[refrigerant.ashrae_name]
    return GLIDE_SERIES_400_DEFAULT if refrigerant.ashrae_name.startswith("R-4") else 0.0


class ThermodynamicEngine:
    """Clausius-Clapeyron calibrado con corrección cerca del punto crítico (Riedel)."""

    @staticmethod
    def calculate_vapor_pressure(refrigerant: Refrigerant, temp_c: float) -> float:
        """Presión absoluta de saturación (bar) a `temp_c`; sobre la temperatura crítica devuelve P crítica."""
        if temp_c >= refrigerant.critical_temp_c:
            return refrigerant.critical_pressure_bar
        T = temp_c + 273.15
        T_b = refrigerant.boiling_point_c + 273.15
        T_c = refrigerant.critical_temp_c + 273.15

        # ln(P / P_atm) = (ΔH_vap / R) · (1/T_b − 1/T)
        p_abs = math.exp(math.log(ATM_BAR) + trouton_factor(refrigerant) * T_b * (1.0 / T_b - 1.0 / T))

        T_r = T / T_c
        if T_r > 0.6:  # suaviza la curva hacia el punto crítico
            p_abs *= 1.0 + 0.15 * math.sin(math.pi * (T_r - 0.6) / 0.4)
        return max(min(p_abs, refrigerant.critical_pressure_bar), MIN_PRESSURE_BAR)
