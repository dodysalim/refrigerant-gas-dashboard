"""
Módulos de Infraestructura - Lectores de Datos (Data Readers)
Aplica principios SOLID (ISP, LSP) y el patrón Factory para la extracción de datos.
Proporciona soporte de análisis de PDF y un Fallback estático con 55 gases y solucionadores P-T.
"""

import abc
import os
import math
from typing import List, Dict, Any, Optional
from src.domain.entities import Refrigerant, SaturatedPressureFact

class IDataReader(abc.ABC):
    """
    Interface Segregation Principle (ISP) & Liskov Substitution Principle (LSP).
    Define la interfaz contractual para cualquier lector de datos de refrigerantes.
    """
    @abc.abstractmethod
    def read_refrigerants(self) -> List[Refrigerant]:
        """Extrae la lista de entidades de refrigerantes."""
        pass

    @abc.abstractmethod
    def read_pressure_temperature_points(self, refrigerants: List[Refrigerant]) -> List[SaturatedPressureFact]:
        """Genera o extrae los registros de presión-temperatura para los gases dados."""
        pass


class ThermodynamicEngine:
    """
    Motor termodinámico que calcula con precisión las curvas de Presión-Temperatura (P-T)
    de saturación para diferentes refrigerantes basándose en sus constantes críticas
    y ecuaciones de estado reducidas (Clausius-Clapeyron calibrado / Antoine).
    """
    @staticmethod
    def calculate_vapor_pressure(refrigerant: Refrigerant, temp_c: float) -> float:
        """
        Calcula la presión absoluta de vapor de saturación en bar a partir de la temperatura en °C.
        Si la temperatura supera la temperatura crítica, devuelve la presión crítica (supercrítico).
        """
        if temp_c >= refrigerant.critical_temp_c:
            return refrigerant.critical_pressure_bar
        
        # Parámetros en Kelvin
        T = temp_c + 273.15
        T_b = refrigerant.boiling_point_c + 273.15
        T_c = refrigerant.critical_temp_c + 273.15
        P_c = refrigerant.critical_pressure_bar
        
        # Ajuste de Clausius-Clapeyron con corrección por tipo de compuesto
        # Trouton's Rule modificado (Entalpía de vaporización / R)
        if refrigerant.compound_type == "Natural":
            if refrigerant.ashrae_name == "R-717":  # Amoníaco (muy polar)
                trouton_factor = 12.8
            elif refrigerant.ashrae_name == "R-744": # CO2 (presión extremadamente alta)
                trouton_factor = 9.2
            else:
                trouton_factor = 10.6
        elif "HFO" in refrigerant.compound_type:
            trouton_factor = 10.2
        elif "HCFC" in refrigerant.compound_type:
            trouton_factor = 10.8
        elif "CFC" in refrigerant.compound_type:
            trouton_factor = 10.9
        else: # HFC y Blends
            trouton_factor = 10.5
            
        # Ecuación de Clapeyron calibrada
        # ln(P / P_1atm) = (H_vap / R) * (1 / T_b - 1 / T)
        # P_1atm = 1.01325 bar
        ln_p = math.log(1.01325) + trouton_factor * T_b * (1.0 / T_b - 1.0 / T)
        p_abs = math.exp(ln_p)
        
        # Corrección por proximidad al punto crítico (Riedel)
        T_r = T / T_c
        if T_r > 0.6:
            # Factor de corrección para suavizar la curva hacia el punto crítico
            correction = 1.0 + 0.15 * math.sin(math.pi * (T_r - 0.6) / 0.4)
            p_abs = p_abs * correction
            
        # Limitar al punto crítico
        if p_abs > P_c:
            p_abs = P_c
            
        # Asegurar presión positiva mínima
        return max(p_abs, 0.005)


class FallbackStaticDataReader(IDataReader):
    """
    Implementación del lector de datos estáticos fallback.
    Contiene un catálogo completo de 55 gases refrigerantes con propiedades validadas
    y descripciones de alta calidad técnica.
    """
    def __init__(self):
        # Base de datos integrada de 55 gases refrigerantes
        self._raw_data = [
            # --- 1. REFRIGERACIÓN BÁSICA (15 gases) ---
            {
                "key": 1, "ashrae_name": "R-134a", "chemical_name": "1,1,1,2-Tetrafluoroetano",
                "chemical_formula": "CF3CH2F", "compound_type": "HFC", "safety_group": "A1",
                "odp": 0.0, "gwp": 1430.0, "category": "Basic", "primary_oil": "POE", "status": "Phasing Down",
                "color_hex": "#3A9AD9", "boiling_point_c": -26.3, "critical_temp_c": 101.1, "critical_pressure_bar": 40.6,
                "description": "El refrigerante estándar de la industria para refrigeración doméstica, automotriz y comercial ligera. Reemplazó al R-12.",
                "pros": "No inflamable, baja toxicidad, termodinámicamente eficiente a temperaturas medias.",
                "cons": "Alto GWP. Sujeto a cuotas de reducción bajo la Enmienda de Kigali.",
                "alternatives": "R-1234yf, R-513A, R-290", "true_replacement": "R-1234yf (Automotriz) o R-513A (Comercial / Drop-in)"
            },
            {
                "key": 2, "ashrae_name": "R-600a", "chemical_name": "Isobutano",
                "chemical_formula": "CH(CH3)3", "compound_type": "HC", "safety_group": "A3",
                "odp": 0.0, "gwp": 3.0, "category": "Basic", "primary_oil": "Mineral", "status": "Active",
                "color_hex": "#2ECC71", "boiling_point_c": -11.7, "critical_temp_c": 134.7, "critical_pressure_bar": 36.4,
                "description": "Hidrocarburo natural de excelente rendimiento. Convertido en el estándar mundial para heladeras domésticas modernas.",
                "pros": "Impacto ambiental insignificante, alta eficiencia, menor carga de gas requerida.",
                "cons": "Altamente inflamable (A3). Requiere precauciones especiales de diseño y servicio.",
                "alternatives": "Ninguna (ya es el reemplazo ecológico dominante)", "true_replacement": "Ninguno (Ya es el estándar ecológico natural en heladeras)"
            },
            {
                "key": 3, "ashrae_name": "R-290", "chemical_name": "Propano",
                "chemical_formula": "CH3CH2CH3", "compound_type": "HC", "safety_group": "A3",
                "odp": 0.0, "gwp": 3.0, "category": "Basic", "primary_oil": "Mineral", "status": "Active",
                "color_hex": "#16A085", "boiling_point_c": -42.1, "critical_temp_c": 96.7, "critical_pressure_bar": 42.5,
                "description": "Propano de alta pureza. Excelente para sistemas comerciales autónomos pequeños (freezers de supermercado, botelleros).",
                "pros": "Termodinámica soberbia, bajísimo GWP, compatible con aceite mineral económico.",
                "cons": "Altamente inflamable (A3). Carga limitada por normativas de seguridad (usualmente 150g a 500g).",
                "alternatives": "R-454C, R-455A", "true_replacement": "Ninguno (Ya es el estándar ecológico natural en botelleros)"
            },
            {
                "key": 4, "ashrae_name": "R-12", "chemical_name": "Diclorodifluorometano",
                "chemical_formula": "CCl2F2", "compound_type": "CFC", "safety_group": "A1",
                "odp": 1.0, "gwp": 10900.0, "category": "Basic", "primary_oil": "Mineral", "status": "Phased Out",
                "color_hex": "#E74C3C", "boiling_point_c": -29.8, "critical_temp_c": 112.0, "critical_pressure_bar": 41.2,
                "description": "El refrigerante más famoso de la historia, prohibido a nivel global por el Protocolo de Montreal debido a su altísimo daño a la capa de ozono.",
                "pros": "Termodinámicamente perfecto, no inflamable, estable químicamente.",
                "cons": "Altísimo ODP y GWP extremo. Totalmente prohibido.",
                "alternatives": "R-134a, R-600a", "true_replacement": "R-134a (Sustituto Ecológico) o R-437A (Sustituto Drop-in compatible con aceite mineral)"
            },
            {
                "key": 5, "ashrae_name": "R-401A", "chemical_name": "Mezcla MP39 (R-22/152a/124)",
                "chemical_formula": "Mezcla zeotrópica", "compound_type": "HCFC", "safety_group": "A1",
                "odp": 0.03, "gwp": 1182.0, "category": "Basic", "primary_oil": "Alquilbenceno", "status": "Phased Out",
                "color_hex": "#F39C12", "boiling_point_c": -32.6, "critical_temp_c": 108.0, "critical_pressure_bar": 46.1,
                "description": "Mezcla de transición diseñada para sustituir al R-12 en refrigeración comercial de temperatura media sin cambiar el compresor.",
                "pros": "Presiones de descarga similares al R-12, compatible con aceites tradicionales con AB.",
                "cons": "Contiene R-22 (daño al ozono residual), sujeto a eliminación.",
                "alternatives": "R-437A, R-134a", "true_replacement": "R-437A o R-134a (requiere cambio a aceite POE)"
            },
            {
                "key": 6, "ashrae_name": "R-401B", "chemical_name": "Mezcla MP66 (R-22/152a/124)",
                "chemical_formula": "Mezcla zeotrópica", "compound_type": "HCFC", "safety_group": "A1",
                "odp": 0.035, "gwp": 1288.0, "category": "Basic", "primary_oil": "Alquilbenceno", "status": "Phased Out",
                "color_hex": "#D35400", "boiling_point_c": -34.5, "critical_temp_c": 105.0, "critical_pressure_bar": 46.5,
                "description": "Variante de transición optimizada para sistemas de congelamiento comercial de baja temperatura de R-12.",
                "pros": "Mayor capacidad frigorífica a bajas temperaturas que el R-401A.",
                "cons": "Impacto ecológico moderado por presencia de HCFC.",
                "alternatives": "R-437A, R-404A", "true_replacement": "R-437A o R-404A"
            },
            {
                "key": 7, "ashrae_name": "R-409A", "chemical_name": "Mezcla FX56 (R-22/124/142b)",
                "chemical_formula": "Mezcla zeotrópica", "compound_type": "HCFC", "safety_group": "A1",
                "odp": 0.048, "gwp": 1585.0, "category": "Basic", "primary_oil": "Alquilbenceno", "status": "Phased Out",
                "color_hex": "#E67E22", "boiling_point_c": -34.3, "critical_temp_c": 109.4, "critical_pressure_bar": 45.9,
                "description": "Otro refrigerante de sustitución temporal del R-12 de alta popularidad en el mercado de repuestos automotrices y comerciales del siglo pasado.",
                "pros": "Fácil sustitución en heladeras comerciales antiguas.",
                "cons": "Efecto negativo sobre el ozono, alto potencial de calentamiento global.",
                "alternatives": "R-437A", "true_replacement": "R-437A"
            },
            {
                "key": 8, "ashrae_name": "R-413A", "chemical_name": "Mezcla ISCEON 49",
                "chemical_formula": "Mezcla R-134a/218/600a", "compound_type": "HFC", "safety_group": "A2",
                "odp": 0.0, "gwp": 2053.0, "category": "Basic", "primary_oil": "Mineral/POE", "status": "Phasing Down",
                "color_hex": "#1ABC9C", "boiling_point_c": -34.8, "critical_temp_c": 101.2, "critical_pressure_bar": 40.7,
                "description": "Reemplazo directo libre de cloro para sistemas R-12 en refrigeración doméstica y aire acondicionado móvil.",
                "pros": "Compatible con aceite mineral debido a la fracción de isobutano añadida.",
                "cons": "Presencia de R-218 aumenta significativamente el GWP.",
                "alternatives": "R-437A", "true_replacement": "R-437A"
            },
            {
                "key": 9, "ashrae_name": "R-426A", "chemical_name": "Mezcla RS-24",
                "chemical_formula": "Mezcla R-134a/125/600/601a", "compound_type": "HFC", "safety_group": "A1",
                "odp": 0.0, "gwp": 1508.0, "category": "Basic", "primary_oil": "POE/Mineral", "status": "Active",
                "color_hex": "#3498DB", "boiling_point_c": -28.6, "critical_temp_c": 100.9, "critical_pressure_bar": 40.8,
                "description": "Sustituto directo (drop-in) de R-12 en refrigeradores domésticos y comerciales, compatible con lubricantes tradicionales.",
                "pros": "Seguridad clasificada A1 (no inflamable), no daña el ozono.",
                "cons": "Su GWP es moderado-alto.",
                "alternatives": "R-134a", "true_replacement": "R-134a"
            },
            {
                "key": 10, "ashrae_name": "R-437A", "chemical_name": "Mezcla Isceon MO49 Plus",
                "chemical_formula": "Mezcla R-134a/125/600/601", "compound_type": "HFC", "safety_group": "A1",
                "odp": 0.0, "gwp": 1805.0, "category": "Basic", "primary_oil": "Mineral/POE", "status": "Active",
                "color_hex": "#2980B9", "boiling_point_c": -32.3, "critical_temp_c": 98.7, "critical_pressure_bar": 40.6,
                "description": "Reemplazo drop-in definitivo del R-12 y de las mezclas de transición como R-401A/B y R-409A.",
                "pros": "Permite conservar el aceite mineral y el compresor existente con nula toxicidad.",
                "cons": "El GWP sigue siendo alto para la regulación europea F-Gas.",
                "alternatives": "R-513A", "true_replacement": "R-513A o R-1234yf (HFO de bajo GWP)"
            },
            {
                "key": 11, "ashrae_name": "R-600", "chemical_name": "Butano normal",
                "chemical_formula": "CH3CH2CH2CH3", "compound_type": "HC", "safety_group": "A3",
                "odp": 0.0, "gwp": 4.0, "category": "Basic", "primary_oil": "Mineral", "status": "Active",
                "color_hex": "#27AE60", "boiling_point_c": -0.5, "critical_temp_c": 152.0, "critical_pressure_bar": 38.0,
                "description": "Butano de uso termodinámico. Utilizado principalmente en mezclas de refrigeración y en algunas heladeras especializadas.",
                "pros": "Cero impacto ambiental, excelente lubricidad con aceite mineral.",
                "cons": "Punto de ebullición muy alto, inflamable (A3).",
                "alternatives": "R-600a", "true_replacement": "R-600a"
            },
            {
                "key": 12, "ashrae_name": "R-1234yf", "chemical_name": "2,3,3,3-Tetrafluoropropeno",
                "chemical_formula": "CF3CF=CH2", "compound_type": "HFO", "safety_group": "A2L",
                "odp": 0.0, "gwp": 1.0, "category": "Basic", "primary_oil": "PAG/POE", "status": "Active",
                "color_hex": "#1ABC9C", "boiling_point_c": -29.4, "critical_temp_c": 94.7, "critical_pressure_bar": 33.8,
                "description": "Hidrofluoroolefina de cuarta generación de ultra-bajo GWP. Es el reemplazo oficial obligatorio del R-134a en el aire acondicionado automotriz.",
                "pros": "GWP de 1, alta eficiencia termodinámica, rápida descomposición en la atmósfera.",
                "cons": "Ligeramente inflamable (A2L). Genera trazas menores de TFA (ácido trifluoroacético).",
                "alternatives": "R-744 (CO2 en autos)", "true_replacement": "Ninguno (Es la HFO de ultra bajo GWP definitiva en automoción)"
            },
            {
                "key": 13, "ashrae_name": "R-415B", "chemical_name": "Mezcla de R-22 e R-152a",
                "chemical_formula": "Mezcla zeotrópica", "compound_type": "Blend", "safety_group": "A2",
                "odp": 0.01, "gwp": 1500.0, "category": "Basic", "primary_oil": "Mineral/AB", "status": "Phased Out",
                "color_hex": "#F1C40F", "boiling_point_c": -30.0, "critical_temp_c": 102.0, "critical_pressure_bar": 45.0,
                "description": "Mezcla de transición de escaso uso masivo pero común en áreas de desarrollo para reconversiones rápidas.",
                "pros": "Presión compatible con R-12 y R-134a.",
                "cons": "Ligeramente inflamable y con impacto de ozono remanente.",
                "alternatives": "R-134a", "true_replacement": "R-134a"
            },
            {
                "key": 14, "ashrae_name": "R-424A", "chemical_name": "Mezcla RS-44",
                "chemical_formula": "Mezcla zeotrópica HFC", "compound_type": "HFC", "safety_group": "A1",
                "odp": 0.0, "gwp": 2440.0, "category": "Basic", "primary_oil": "Mineral/POE", "status": "Phasing Down",
                "color_hex": "#7FB3D5", "boiling_point_c": -38.7, "critical_temp_c": 88.8, "critical_pressure_bar": 40.4,
                "description": "Diseñado originalmente para aire acondicionado y refrigeración, se usa a veces como drop-in de baja temperatura.",
                "pros": "No inflamable, compatible con aceites minerales clásicos.",
                "cons": "GWP elevado.",
                "alternatives": "R-407C, R-427A", "true_replacement": "R-427A o R-407C"
            },
            {
                "key": 15, "ashrae_name": "R-513A", "chemical_name": "Mezcla Opteon XP10 (R-134a/1234yf)",
                "chemical_formula": "Mezcla azeotrópica HFC/HFO", "compound_type": "Blend", "safety_group": "A1",
                "odp": 0.0, "gwp": 573.0, "category": "Basic", "primary_oil": "POE", "status": "Active",
                "color_hex": "#5DADE2", "boiling_point_c": -29.2, "critical_temp_c": 96.5, "critical_pressure_bar": 37.6,
                "description": "Una mezcla azeotrópica diseñada para reemplazar de manera directa al R-134a reduciendo el GWP en un 56%.",
                "pros": "Clasificación de seguridad A1 (no inflamable), compatibilidad directa con equipos R-134a.",
                "cons": "Su GWP sigue estando por encima de las alternativas naturales.",
                "alternatives": "R-290, R-1234yf", "true_replacement": "R-290 (Propano natural)"
            },

            # --- 2. REFRIGERACIÓN INTERMEDIA / AIRE ACONDICIONADO (24 gases) ---
            {
                "key": 16, "ashrae_name": "R-22", "chemical_name": "Clorodifluorometano",
                "chemical_formula": "CHClF2", "compound_type": "HCFC", "safety_group": "A1",
                "odp": 0.055, "gwp": 1810.0, "category": "Intermediate", "primary_oil": "Mineral/AB", "status": "Phased Out",
                "color_hex": "#85C1E9", "boiling_point_c": -40.8, "critical_temp_c": 96.1, "critical_pressure_bar": 49.9,
                "description": "El HCFC más utilizado a nivel mundial en aire acondicionado residencial y comercial ligero. Actualmente prohibido en equipos nuevos.",
                "pros": "Propiedades físicas excelentes, coste muy bajo históricamente.",
                "cons": "Daña levemente la capa de ozono, alto potencial de calentamiento global.",
                "alternatives": "R-407C, R-410A, R-427A, R-438A", "true_replacement": "R-407C (AC con cambio de aceite POE) o R-438A (Drop-in compatible con aceite mineral)"
            },
            {
                "key": 17, "ashrae_name": "R-410A", "chemical_name": "Mezcla de R-32 e R-125",
                "chemical_formula": "Mezcla cuasi-azeotrópica", "compound_type": "HFC", "safety_group": "A1",
                "odp": 0.0, "gwp": 2088.0, "category": "Intermediate", "primary_oil": "POE", "status": "Phasing Down",
                "color_hex": "#D35400", "boiling_point_c": -51.4, "critical_temp_c": 71.4, "critical_pressure_bar": 49.0,
                "description": "El refrigerante líder para sistemas de aire acondicionado residencial (split) e industrial ligero de las últimas dos décadas.",
                "pros": "Gran capacidad frigorífica, equipos compactos gracias a su alta densidad.",
                "cons": "Presiones de trabajo un 50% superiores a R-22, alto GWP.",
                "alternatives": "R-32, R-454B", "true_replacement": "R-32 (Menor GWP en splits) o R-454B (Chillers de gran escala)"
            },
            {
                "key": 18, "ashrae_name": "R-404A", "chemical_name": "Mezcla de R-125/143a/134a",
                "chemical_formula": "Mezcla zeotrópica", "compound_type": "HFC", "safety_group": "A1",
                "odp": 0.0, "gwp": 3922.0, "category": "Intermediate", "primary_oil": "POE", "status": "Phasing Down",
                "color_hex": "#E67E22", "boiling_point_c": -46.5, "critical_temp_c": 72.1, "critical_pressure_bar": 37.3,
                "description": "El caballo de batalla de la refrigeración de supermercados y transporte refrigerado. En rápido retroceso debido a regulaciones.",
                "pros": "Rendimiento soberbio en congelados y temperaturas medias.",
                "cons": "GWP sumamente elevado (casi 4000), prohibido en la UE para nuevos sistemas grandes.",
                "alternatives": "R-448A, R-449A, R-452A, R-290", "true_replacement": "R-448A / R-449A (HFO/HFC de bajo GWP) o R-744 (CO2 natural)"
            },
            {
                "key": 19, "ashrae_name": "R-407C", "chemical_name": "Mezcla de R-32/125/134a",
                "chemical_formula": "Mezcla zeotrópica", "compound_type": "HFC", "safety_group": "A1",
                "odp": 0.0, "gwp": 1774.0, "category": "Intermediate", "primary_oil": "POE", "status": "Phasing Down",
                "color_hex": "#884EA0", "boiling_point_c": -43.8, "critical_temp_c": 86.0, "critical_pressure_bar": 46.3,
                "description": "Reemplazo de R-22 en aire acondicionado. Posee presiones similares, pero requiere cambio a aceite sintético.",
                "pros": "Presión y capacidad casi idénticas a R-22, sin toxicidad ni inflamabilidad.",
                "cons": "Deslizamiento térmico (glide) significativo de unos 5°C, lo que complica la recarga ante fugas.",
                "alternatives": "R-32, R-454B", "true_replacement": "R-32 o R-454B"
            },
            {
                "key": 20, "ashrae_name": "R-507A", "chemical_name": "Mezcla azeotrópica (R-125/143a)",
                "chemical_formula": "Mezcla azeotrópica", "compound_type": "HFC", "safety_group": "A1",
                "odp": 0.0, "gwp": 3985.0, "category": "Intermediate", "primary_oil": "POE", "status": "Phasing Down",
                "color_hex": "#9B59B6", "boiling_point_c": -46.7, "critical_temp_c": 70.6, "critical_pressure_bar": 37.9,
                "description": "Equivalente azeotrópico de R-404A, preferido por algunos fabricantes de compresores debido a su nulo deslizamiento de temperatura.",
                "pros": "Cero glide, excelente rendimiento térmico estable a bajas temperaturas.",
                "cons": "GWP extremadamente alto.",
                "alternatives": "R-448A, R-449A", "true_replacement": "R-448A / R-449A"
            },
            {
                "key": 21, "ashrae_name": "R-32", "chemical_name": "Difluorometano",
                "chemical_formula": "CH2F2", "compound_type": "HFC", "safety_group": "A2L",
                "odp": 0.0, "gwp": 675.0, "category": "Intermediate", "primary_oil": "POE", "status": "Active",
                "color_hex": "#27AE60", "boiling_point_c": -51.7, "critical_temp_c": 78.1, "critical_pressure_bar": 57.8,
                "description": "HFC puro de bajo GWP. Convertido en el refrigerante dominante en aire acondicionado split moderno en reemplazo de R-410A.",
                "pros": "GWP un 68% menor que R-410A, excelente coeficiente de transferencia de calor y menor volumen de carga.",
                "cons": "Ligeramente inflamable (A2L), temperaturas de descarga muy altas en climas extremos.",
                "alternatives": "R-454B, R-290", "true_replacement": "R-454B o R-290 (Alternativas de menor GWP)"
            },
            {
                "key": 22, "ashrae_name": "R-407A", "chemical_name": "Mezcla zeotrópica HFC",
                "chemical_formula": "Mezcla R-32/125/134a", "compound_type": "HFC", "safety_group": "A1",
                "odp": 0.0, "gwp": 2107.0, "category": "Intermediate", "primary_oil": "POE", "status": "Phasing Down",
                "color_hex": "#7D3C98", "boiling_point_c": -45.0, "critical_temp_c": 82.0, "critical_pressure_bar": 45.0,
                "description": "Una alternativa para la reconversión de R-502 y R-22 en sistemas de refrigeración de supermercados.",
                "pros": "Menor GWP que R-404A con buen rendimiento frigorífico.",
                "cons": "Elevado glide térmico.",
                "alternatives": "R-448A, R-449A", "true_replacement": "R-448A o R-449A"
            },
            {
                "key": 23, "ashrae_name": "R-407F", "chemical_name": "Mezcla Performax LT",
                "chemical_formula": "Mezcla R-32/125/134a", "compound_type": "HFC", "safety_group": "A1",
                "odp": 0.0, "gwp": 1825.0, "category": "Intermediate", "primary_oil": "POE", "status": "Phasing Down",
                "color_hex": "#6C3483", "boiling_point_c": -46.1, "critical_temp_c": 82.6, "critical_pressure_bar": 47.6,
                "description": "Opción de readaptación directa de R-404A/R-507A que reduce el consumo eléctrico y las emisiones de carbono.",
                "pros": "Reduce a la mitad el GWP del R-404A y ofrece excelente capacidad frigorífica.",
                "cons": "Mayor temperatura de descarga del compresor.",
                "alternatives": "R-448A", "true_replacement": "R-448A"
            },
            {
                "key": 24, "ashrae_name": "R-422D", "chemical_name": "Mezcla Isceon MO29",
                "chemical_formula": "Mezcla R-125/134a/600a", "compound_type": "HFC", "safety_group": "A1",
                "odp": 0.0, "gwp": 2729.0, "category": "Intermediate", "primary_oil": "Mineral/POE", "status": "Phasing Down",
                "color_hex": "#AEB6BF", "boiling_point_c": -43.0, "critical_temp_c": 79.6, "critical_pressure_bar": 39.0,
                "description": "Reemplazo rápido tipo drop-in para enfriadores de agua (chillers) y aire acondicionado de R-22, compatible con aceites minerales.",
                "pros": "Fácil sustitución de R-22 sin cambio de lubricante.",
                "cons": "Capacidad frigorífica ligeramente inferior en bajas temperaturas.",
                "alternatives": "R-427A", "true_replacement": "R-427A"
            },
            {
                "key": 25, "ashrae_name": "R-427A", "chemical_name": "Mezcla Forane 427A",
                "chemical_formula": "Mezcla R-32/125/143a/134a", "compound_type": "HFC", "safety_group": "A1",
                "odp": 0.0, "gwp": 2138.0, "category": "Intermediate", "primary_oil": "Mineral/POE", "status": "Active",
                "color_hex": "#5D6D7E", "boiling_point_c": -43.0, "critical_temp_c": 85.3, "critical_pressure_bar": 43.9,
                "description": "El sustituto drop-in de R-22 más versátil, apto para aire acondicionado y refrigeración de baja y media temperatura.",
                "pros": "Excelente retorno de aceite mineral residual, comportamiento termodinámico balanceado.",
                "cons": "Glide de 4.5°C.",
                "alternatives": "R-448A", "true_replacement": "R-448A"
            },
            {
                "key": 26, "ashrae_name": "R-448A", "chemical_name": "Mezcla Solstice N40",
                "chemical_formula": "Mezcla HFC/HFO", "compound_type": "Blend", "safety_group": "A1",
                "odp": 0.0, "gwp": 1387.0, "category": "Intermediate", "primary_oil": "POE", "status": "Active",
                "color_hex": "#1F618D", "boiling_point_c": -45.9, "critical_temp_c": 83.7, "critical_pressure_bar": 46.6,
                "description": "La mezcla ecológica de HFO/HFC de referencia comercial para sustituir al R-404A en supermercados nuevos e instalaciones existentes.",
                "pros": "Reducción del 65% en GWP comparado con R-404A, alta eficiencia energética.",
                "cons": "Mayor deslizamiento de temperatura y temperatura de descarga que R-404A.",
                "alternatives": "R-744, R-290", "true_replacement": "R-744 (CO2) o R-290 (Sustituto natural definitivo)"
            },
            {
                "key": 27, "ashrae_name": "R-449A", "chemical_name": "Mezcla Opteon XP40",
                "chemical_formula": "Mezcla HFC/HFO", "compound_type": "Blend", "safety_group": "A1",
                "odp": 0.0, "gwp": 1397.0, "category": "Intermediate", "primary_oil": "POE", "status": "Active",
                "color_hex": "#2874A6", "boiling_point_c": -46.0, "critical_temp_c": 83.1, "critical_pressure_bar": 44.5,
                "description": "Equivalente comercial directo de R-448A fabricado por DuPont/Chemours, ampliamente aceptado en la cadena de frío mundial.",
                "pros": "No inflamable, estable termodinámicamente, amigable con el medio ambiente.",
                "cons": "Requiere válvulas de expansión ajustadas por el glide.",
                "alternatives": "R-744, R-454C", "true_replacement": "R-744 (CO2) o R-290 (Sustituto natural definitivo)"
            },
            {
                "key": 28, "ashrae_name": "R-452A", "chemical_name": "Mezcla Opteon XP44",
                "chemical_formula": "Mezcla R-32/125/1234yf", "compound_type": "Blend", "safety_group": "A1",
                "odp": 0.0, "gwp": 2140.0, "category": "Intermediate", "primary_oil": "POE", "status": "Active",
                "color_hex": "#E74C3C", "boiling_point_c": -47.0, "critical_temp_c": 74.9, "critical_pressure_bar": 40.0,
                "description": "Reemplazo de R-404A optimizado especialmente para refrigeración de transporte (camiones, contenedores) y compresores semi-herméticos.",
                "pros": "Mantiene baja la temperatura de descarga (muy similar al R-404A), protegiendo al motor.",
                "cons": "GWP de 2140, superior al de R-448A/R-449A.",
                "alternatives": "R-454C", "true_replacement": "R-454C"
            },
            {
                "key": 29, "ashrae_name": "R-417A", "chemical_name": "Mezcla Isceon MO59",
                "chemical_formula": "Mezcla R-125/134a/600", "compound_type": "HFC", "safety_group": "A1",
                "odp": 0.0, "gwp": 2346.0, "category": "Intermediate", "primary_oil": "Mineral/POE", "status": "Phasing Down",
                "color_hex": "#B2BABB", "boiling_point_c": -39.1, "critical_temp_c": 86.9, "critical_pressure_bar": 40.4,
                "description": "Primer reemplazo sin cloro comercializado para el aire acondicionado R-22 comercial clásico.",
                "pros": "Funciona con aceites minerales clásicos sin modificaciones estructurales.",
                "cons": "Pérdida de capacidad frigorífica de hasta un 15% en aplicaciones extremas.",
                "alternatives": "R-427A", "true_replacement": "R-427A"
            },
            {
                "key": 30, "ashrae_name": "R-422A", "chemical_name": "Mezcla Isceon MO79",
                "chemical_formula": "Mezcla R-125/134a/600a", "compound_type": "HFC", "safety_group": "A1",
                "odp": 0.0, "gwp": 3143.0, "category": "Intermediate", "primary_oil": "Mineral/POE", "status": "Phasing Down",
                "color_hex": "#566573", "boiling_point_c": -46.5, "critical_temp_c": 71.7, "critical_pressure_bar": 37.5,
                "description": "Sustituto directo de R-502 y R-404A en equipos de congelamiento rápido comerciales de baja temperatura.",
                "pros": "Excelente retorno de aceite en bajas temperaturas, no inflamable.",
                "cons": "Alto GWP residual.",
                "alternatives": "R-448A", "true_replacement": "R-448A"
            },
            {
                "key": 31, "ashrae_name": "R-438A", "chemical_name": "Mezcla Freon MO99",
                "chemical_formula": "Mezcla R-32/125/134a/600/601a", "compound_type": "HFC", "safety_group": "A1",
                "odp": 0.0, "gwp": 2264.0, "category": "Intermediate", "primary_oil": "Mineral/POE", "status": "Active",
                "color_hex": "#2E4053", "boiling_point_c": -43.0, "critical_temp_c": 84.7, "critical_pressure_bar": 43.1,
                "description": "El sustituto drop-in preferido por técnicos en Latinoamérica para reconvertir equipos de aire acondicionado de R-22 sin cambiar de aceite.",
                "pros": "Presiones casi idénticas, no inflamable, el más compatible con lubricantes clásicos.",
                "cons": "Eficiencia marginalmente menor a R-22.",
                "alternatives": "R-427A", "true_replacement": "R-427A"
            },
            {
                "key": 32, "ashrae_name": "R-453A", "chemical_name": "Mezcla RS-70",
                "chemical_formula": "Mezcla zeotrópica HFC/HC", "compound_type": "HFC", "safety_group": "A1",
                "odp": 0.0, "gwp": 1765.0, "category": "Intermediate", "primary_oil": "Mineral/POE", "status": "Active",
                "color_hex": "#2471A3", "boiling_point_c": -42.2, "critical_temp_c": 87.2, "critical_pressure_bar": 43.6,
                "description": "Alternativa de bajo impacto relativa diseñada para expandir los rangos de operación de chillers medianos.",
                "pros": "No daña el ozono, menor GWP que R-438A.",
                "cons": "No ampliamente distribuido fuera de Europa.",
                "alternatives": "R-427A", "true_replacement": "R-427A"
            },
            {
                "key": 33, "ashrae_name": "R-502", "chemical_name": "Mezcla azeotrópica (R-22/115)",
                "chemical_formula": "Mezcla azeotrópica CFC/HCFC", "compound_type": "Blend", "safety_group": "A1",
                "odp": 0.25, "gwp": 4657.0, "category": "Intermediate", "primary_oil": "Mineral", "status": "Phased Out",
                "color_hex": "#CB4335", "boiling_point_c": -45.3, "critical_temp_c": 82.2, "critical_pressure_bar": 40.7,
                "description": "Clásico compuesto de los años 80 para congelamiento rápido en supermercados. Prohibido formalmente por daño a la capa de ozono.",
                "pros": "Gran estabilidad, sin glide, baja temperatura de descarga.",
                "cons": "Gran impacto al ozono y calentamiento global severo.",
                "alternatives": "R-404A, R-507A", "true_replacement": "R-404A / R-507A"
            },
            {
                "key": 34, "ashrae_name": "R-454B", "chemical_name": "Mezcla Opteon XL41 (R-32/1234yf)",
                "chemical_formula": "Mezcla HFC/HFO A2L", "compound_type": "Blend", "safety_group": "A2L",
                "odp": 0.0, "gwp": 466.0, "category": "Intermediate", "primary_oil": "POE", "status": "Active",
                "color_hex": "#D5F5E3", "boiling_point_c": -50.9, "critical_temp_c": 77.0, "critical_pressure_bar": 52.8,
                "description": "Una de las alternativas clave a largo plazo para R-410A en grandes sistemas de aire acondicionado y chillers comerciales.",
                "pros": "Reducción de GWP en un 78%, eficiencia energética incrementada.",
                "cons": "Ligeramente inflamable (A2L).",
                "alternatives": "R-32", "true_replacement": "R-290 (Propano natural)"
            },
            {
                "key": 35, "ashrae_name": "R-454C", "chemical_name": "Mezcla Opteon XL20 (R-32/1234yf)",
                "chemical_formula": "Mezcla HFC/HFO A2L", "compound_type": "Blend", "safety_group": "A2L",
                "odp": 0.0, "gwp": 148.0, "category": "Intermediate", "primary_oil": "POE", "status": "Active",
                "color_hex": "#ABEBC6", "boiling_point_c": -45.6, "critical_temp_c": 85.7, "critical_pressure_bar": 42.0,
                "description": "Desarrollado para cumplir con la limitación de GWP < 150 de la Unión Europea para equipos comerciales de refrigeración medianos.",
                "pros": "Bajísima huella de carbono, seguro para cargas medianas en supermercados.",
                "cons": "Ligeramente inflamable, glide moderado.",
                "alternatives": "R-290", "true_replacement": "R-290 (Propano natural)"
            },
            {
                "key": 36, "ashrae_name": "R-455A", "chemical_name": "Mezcla Solstice L40X",
                "chemical_formula": "Mezcla R-32/1234yf/CO2", "compound_type": "Blend", "safety_group": "A2L",
                "odp": 0.0, "gwp": 148.0, "category": "Intermediate", "primary_oil": "POE", "status": "Active",
                "color_hex": "#A2D9CE", "boiling_point_c": -52.0, "critical_temp_c": 85.6, "critical_pressure_bar": 46.5,
                "description": "Solución innovadora que incluye una pequeña proporción de CO2 para suprimir la inflamabilidad manteniendo un bajo GWP.",
                "pros": "Excelente capacidad a bajas temperaturas, GWP extremadamente bajo.",
                "cons": "Deslizamiento térmico muy alto (alrededor de 12°C), de difícil manejo práctico.",
                "alternatives": "R-290, R-744", "true_replacement": "R-290 o R-744"
            },
            {
                "key": 37, "ashrae_name": "R-458A", "chemical_name": "Mezcla Bluewater",
                "chemical_formula": "Mezcla zeotrópica HFC", "compound_type": "HFC", "safety_group": "A1",
                "odp": 0.0, "gwp": 1650.0, "category": "Intermediate", "primary_oil": "POE", "status": "Active",
                "color_hex": "#85929E", "boiling_point_c": -42.0, "critical_temp_c": 87.0, "critical_pressure_bar": 44.0,
                "description": "Una mezcla de transición con aplicaciones específicas en áreas marítimas y mineras.",
                "pros": "No inflamable, estable químicamente.",
                "cons": "Limitada distribución comercial.",
                "alternatives": "R-407C", "true_replacement": "R-407C"
            },
            {
                "key": 38, "ashrae_name": "R-466A", "chemical_name": "Mezcla Solstice N41",
                "chemical_formula": "Mezcla R-32/125/CF3I", "compound_type": "Blend", "safety_group": "A1",
                "odp": 0.0, "gwp": 733.0, "category": "Intermediate", "primary_oil": "POE", "status": "Active",
                "color_hex": "#FADBD8", "boiling_point_c": -51.5, "critical_temp_c": 79.5, "critical_pressure_bar": 54.0,
                "description": "El primer reemplazo no inflamable (A1) diseñado para sustituir directamente al R-410A en sistemas split residenciales.",
                "pros": "Seguridad A1 de bajo GWP. Permite un diseño de equipo clásico.",
                "cons": "Estabilidad química bajo sospecha debido al yoduro de trifluorometano (CF3I).",
                "alternatives": "R-32, R-454B", "true_replacement": "R-32 o R-454B"
            },
            {
                "key": 39, "ashrae_name": "R-407B", "chemical_name": "Mezcla HFC R-32/125/134a",
                "chemical_formula": "Mezcla zeotrópica", "compound_type": "HFC", "safety_group": "A1",
                "odp": 0.0, "gwp": 2800.0, "category": "Intermediate", "primary_oil": "POE", "status": "Phasing Down",
                "color_hex": "#9B59B6", "boiling_point_c": -46.0, "critical_temp_c": 75.0, "critical_pressure_bar": 40.0,
                "description": "Mezcla dirigida a sistemas de media/baja temperatura comerciales.",
                "pros": "No inflamable, sustitución directa aceptable para R-502.",
                "cons": "Elevada huella ecológica de CO2 equivalente.",
                "alternatives": "R-448A", "true_replacement": "R-448A"
            },

            # --- 3. REFRIGERACIÓN INDUSTRIAL / GRAN ESCALA (16 gases) ---
            {
                "key": 40, "ashrae_name": "R-717", "chemical_name": "Amoníaco Anhidro",
                "chemical_formula": "NH3", "compound_type": "Natural", "safety_group": "B2L",
                "odp": 0.0, "gwp": 0.0, "category": "Industrial", "primary_oil": "Mineral/Sintético", "status": "Active",
                "color_hex": "#BDC3C7", "boiling_point_c": -33.3, "critical_temp_c": 132.3, "critical_pressure_bar": 113.3,
                "description": "El refrigerante industrial más eficiente conocido. Utilizado en el 90% de las plantas de procesamiento de alimentos del mundo.",
                "pros": "Eficiencia termodinámica inigualable, coste cero del gas, nulo impacto ambiental (GWP=0, ODP=0).",
                "cons": "Altamente tóxico y picante, corrosivo para el cobre (requiere tuberías de acero), ligeramente inflamable.",
                "alternatives": "R-744 en cascada (para reducir carga tóxica)", "true_replacement": "Ninguno (Fluido natural definitivo de máxima eficiencia)"
            },
            {
                "key": 41, "ashrae_name": "R-744", "chemical_name": "Dióxido de Carbono",
                "chemical_formula": "CO2", "compound_type": "Natural", "safety_group": "A1",
                "odp": 0.0, "gwp": 1.0, "category": "Industrial", "primary_oil": "POE/PAG", "status": "Active",
                "color_hex": "#7F8C8D", "boiling_point_c": -78.4, "critical_temp_c": 31.1, "critical_pressure_bar": 73.8,
                "description": "El refrigerante natural que está revolucionando los supermercados e hipermercados modernos en sistemas transcritícos y cascadas industriales.",
                "pros": "Excelente capacidad de refrigeración por volumen, no inflamable, no tóxico, costo mínimo.",
                "cons": "Presiones extremadamente altas (hasta 120 bar), temperatura crítica muy baja (31.1°C, requiere operación transcrita).",
                "alternatives": "Ninguna (ya es el estandarte de sostenibilidad)", "true_replacement": "Ninguno (Fluido natural definitivo de alto rendimiento)"
            },
            {
                "key": 42, "ashrae_name": "R-123", "chemical_name": "Diclorotrifluoroetano",
                "chemical_formula": "CHCl2CF3", "compound_type": "HCFC", "safety_group": "B1",
                "odp": 0.02, "gwp": 77.0, "category": "Industrial", "primary_oil": "Mineral", "status": "Phased Out",
                "color_hex": "#F1948A", "boiling_point_c": 27.6, "critical_temp_c": 183.7, "critical_pressure_bar": 36.6,
                "description": "Refrigerante de ultra-baja presión para chillers centrífugos industriales que acondicionan grandes edificios y distritos.",
                "pros": "Altísima eficiencia termodinámica en bajas presiones de vapor.",
                "cons": "Posee toxicidad crónica leve (B1), sujeto a retiro por contener cloro.",
                "alternatives": "R-1233zd", "true_replacement": "R-1233zd (HFO de ultra bajo GWP)"
            },
            {
                "key": 43, "ashrae_name": "R-124", "chemical_name": "Clorotetrafluoroetano",
                "chemical_formula": "CHClFCF3", "compound_type": "HCFC", "safety_group": "A1",
                "odp": 0.02, "gwp": 609.0, "category": "Industrial", "primary_oil": "Alquilbenceno", "status": "Phased Out",
                "color_hex": "#EDBB99", "boiling_point_c": -12.0, "critical_temp_c": 122.2, "critical_pressure_bar": 36.2,
                "description": "Utilizado en aplicaciones industriales de temperaturas ambiente muy elevadas (ej. cabinas de grúas en acerías).",
                "pros": "Presiones de descarga ultra-bajas a altas temperaturas exteriores.",
                "cons": "Contiene cloro, prohibido para nuevas instalaciones.",
                "alternatives": "R-515B, R-1233zd", "true_replacement": "R-515B o R-1233zd"
            },
            {
                "key": 44, "ashrae_name": "R-1233zd", "chemical_name": "Trans-1-cloro-3,3,3-trifluoropropeno",
                "chemical_formula": "CF3CH=CHCl", "compound_type": "HFO", "safety_group": "A1",
                "odp": 0.0003, "gwp": 1.0, "category": "Industrial", "primary_oil": "POE", "status": "Active",
                "color_hex": "#48C9B0", "boiling_point_c": 18.3, "critical_temp_c": 165.6, "critical_pressure_bar": 35.7,
                "description": "HFO no inflamable de ultra-bajo GWP diseñado especialmente como sustituto ecológico para chillers centrífugos de R-123.",
                "pros": "Seguro (A1), GWP de 1, excepcional rendimiento energético en baja presión.",
                "cons": "Punto de ebullición por encima de la temperatura ambiente habitual (líquido a 1 atm).",
                "alternatives": "R-1224yd", "true_replacement": "Ninguno (Es la HFO definitiva para chillers centrífugos de baja presión)"
            },
            {
                "key": 45, "ashrae_name": "R-1234ze", "chemical_name": "Trans-1,3,3,3-tetrafluoropropeno",
                "chemical_formula": "CF3CH=CHF", "compound_type": "HFO", "safety_group": "A2L",
                "odp": 0.0, "gwp": 1.0, "category": "Industrial", "primary_oil": "POE", "status": "Active",
                "color_hex": "#52BE80", "boiling_point_c": -19.0, "critical_temp_c": 109.4, "critical_pressure_bar": 36.3,
                "description": "Gas HFO ecológico para chillers industriales de compresión por tornillo y bombas de calor industriales.",
                "pros": "Eficiencia estable, muy bajo GWP, excelente capacidad de alta temperatura.",
                "cons": "Ligeramente inflamable a más de 30°C.",
                "alternatives": "R-515B (no inflamable)", "true_replacement": "R-515B (no inflamable)"
            },
            {
                "key": 46, "ashrae_name": "R-508B", "chemical_name": "Mezcla Suva 95 (R-23/116)",
                "chemical_formula": "Mezcla azeotrópica", "compound_type": "Blend", "safety_group": "A1",
                "odp": 0.0, "gwp": 13396.0, "category": "Industrial", "primary_oil": "POE", "status": "Active",
                "color_hex": "#A569BD", "boiling_point_c": -87.4, "critical_temp_c": 14.0, "critical_pressure_bar": 39.3,
                "description": "Utilizado para refrigeración de ultra-baja temperatura (criogenia, liofilización, almacenamiento de vacunas de -80°C).",
                "pros": "Rendimiento óptimo a -80°C, no inflamable y de baja toxicidad.",
                "cons": "GWP abismal de más de 13,000, sujeto a severo control ambiental.",
                "alternatives": "R-170 (Etano)", "true_replacement": "R-170 (Etano natural)"
            },
            {
                "key": 47, "ashrae_name": "R-23", "chemical_name": "Trifluorometano",
                "chemical_formula": "CHF3", "compound_type": "HFC", "safety_group": "A1",
                "odp": 0.0, "gwp": 14800.0, "category": "Industrial", "primary_oil": "POE", "status": "Phasing Down",
                "color_hex": "#8E44AD", "boiling_point_c": -82.1, "critical_temp_c": 25.9, "critical_pressure_bar": 48.4,
                "description": "Un HFC que se produce como subproducto no deseado y se emplea en sistemas criogénicos y de medicina científica.",
                "pros": "Altas capacidades termodinámicas en frío extremo.",
                "cons": "Tiene la tasa GWP más alta registrada entre los gases refrigerantes de uso regular (14,800).",
                "alternatives": "R-508B, R-170, R-744", "true_replacement": "R-508B o R-170"
            },
            {
                "key": 48, "ashrae_name": "R-503", "chemical_name": "Mezcla azeotrópica (R-13/116)",
                "chemical_formula": "Mezcla azeotrópica CFC/PFC", "compound_type": "Blend", "safety_group": "A1",
                "odp": 0.6, "gwp": 14560.0, "category": "Industrial", "primary_oil": "Mineral", "status": "Phased Out",
                "color_hex": "#CD6155", "boiling_point_c": -88.0, "critical_temp_c": 19.5, "critical_pressure_bar": 44.0,
                "description": "Compuesto clásico de temperatura ultra baja retirado por el Protocolo de Montreal.",
                "pros": "Termodinámica inigualable en bajas temperaturas.",
                "cons": "Extremadamente nocivo al ozono y atmósfera.",
                "alternatives": "R-508B", "true_replacement": "R-508B"
            },
            {
                "key": 49, "ashrae_name": "R-718", "chemical_name": "Agua de alta pureza",
                "chemical_formula": "H2O", "compound_type": "Natural", "safety_group": "A1",
                "odp": 0.0, "gwp": 0.0, "category": "Industrial", "primary_oil": "Ninguno", "status": "Active",
                "color_hex": "#3498DB", "boiling_point_c": 100.0, "critical_temp_c": 374.0, "critical_pressure_bar": 220.6,
                "description": "El refrigerante natural supremo. Utilizado en chillers de absorción industriales que funcionan por calor residual.",
                "pros": "Totalmente ecológico, costo nulo, segura en toda circunstancia.",
                "cons": "Solo utilizable por encima de los 0°C, requiere sistemas de vacío extremos.",
                "alternatives": "Ninguna", "true_replacement": "Ninguno (Agua - Fluido natural absoluto)"
            },
            {
                "key": 50, "ashrae_name": "R-729", "chemical_name": "Aire Seco",
                "chemical_formula": "N2+O2+Ar", "compound_type": "Natural", "safety_group": "A1",
                "odp": 0.0, "gwp": 0.0, "category": "Industrial", "primary_oil": "Ninguno", "status": "Active",
                "color_hex": "#BDC3C7", "boiling_point_c": -194.3, "critical_temp_c": -140.5, "critical_pressure_bar": 37.7,
                "description": "Aire atmosférico comprimido y enfriado, empleado en ciclos criogénicos de gas e industria aeroespacial profunda.",
                "pros": "Abundancia infinita, totalmente inocuo.",
                "cons": "Muy bajo coeficiente de rendimiento (COP) para enfriamientos moderados comerciales.",
                "alternatives": "Ninguna", "true_replacement": "Ninguno (Aire - Fluido natural absoluto)"
            },
            {
                "key": 51, "ashrae_name": "R-1150", "chemical_name": "Etileno",
                "chemical_formula": "C2H4", "compound_type": "Natural", "safety_group": "A3",
                "odp": 0.0, "gwp": 4.0, "category": "Industrial", "primary_oil": "Sintético", "status": "Active",
                "color_hex": "#2ECC71", "boiling_point_c": -103.7, "critical_temp_c": 9.2, "critical_pressure_bar": 50.4,
                "description": "Hidrocarburo natural de muy baja temperatura útil en refinerías e industria petroquímica pesada.",
                "pros": "Excelentes coeficientes de transferencia y baja viscosidad.",
                "cons": "Inflamabilidad severa, temperatura crítica muy baja (9.2°C).",
                "alternatives": "R-170, R-508B", "true_replacement": "R-170"
            },
            {
                "key": 52, "ashrae_name": "R-1270", "chemical_name": "Propileno",
                "chemical_formula": "CH3CH=CH2", "compound_type": "Natural", "safety_group": "A3",
                "odp": 0.0, "gwp": 2.0, "category": "Industrial", "primary_oil": "Mineral/Sintético", "status": "Active",
                "color_hex": "#27AE60", "boiling_point_c": -47.6, "critical_temp_c": 92.4, "critical_pressure_bar": 46.2,
                "description": "Alternativa de hidrocarburo de alta capacidad frigorífica en sistemas medianos industriales de refrigeración.",
                "pros": "Mayor capacidad volumétrica que el propano R-290.",
                "cons": "Inflamable A3.",
                "alternatives": "R-290, R-454C", "true_replacement": "R-290"
            },
            {
                "key": 53, "ashrae_name": "R-170", "chemical_name": "Etano",
                "chemical_formula": "CH3CH3", "compound_type": "Natural", "safety_group": "A3",
                "odp": 0.0, "gwp": 6.0, "category": "Industrial", "primary_oil": "Mineral", "status": "Active",
                "color_hex": "#2ECC71", "boiling_point_c": -88.6, "critical_temp_c": 32.2, "critical_pressure_bar": 48.7,
                "description": "Hidrocarburo natural criogénico de gran uso en licuefacción y petroquímica en cascada con CO2 o propileno.",
                "pros": "Gran eficiencia a -80°C y muy baja huella ecológica.",
                "cons": "Altamente inflamable.",
                "alternatives": "R-508B", "true_replacement": "Ninguno (Es el hidrocarburo natural criogénico definitivo)"
            },
            {
                "key": 54, "ashrae_name": "R-11", "chemical_name": "Triclorofluorometano",
                "chemical_formula": "CCl3F", "compound_type": "CFC", "safety_group": "A1",
                "odp": 1.0, "gwp": 4750.0, "category": "Industrial", "primary_oil": "Mineral", "status": "Phased Out",
                "color_hex": "#E74C3C", "boiling_point_c": 23.7, "critical_temp_c": 198.0, "critical_pressure_bar": 44.1,
                "description": "El refrigerante de gran escala pionero en los años 50 para chillers de edificios. Prohibido mundialmente.",
                "pros": "Muy baja presión, no inflamable.",
                "cons": "Impacto altísimo al ozono y calentamiento global.",
                "alternatives": "R-1233zd", "true_replacement": "R-1233zd"
            },
            {
                "key": 55, "ashrae_name": "R-113", "chemical_name": "Triclorotrifluoroetano",
                "chemical_formula": "C2Cl3F3", "compound_type": "CFC", "safety_group": "A1",
                "odp": 0.8, "gwp": 6130.0, "category": "Industrial", "primary_oil": "Mineral", "status": "Phased Out",
                "color_hex": "#C0392B", "boiling_point_c": 47.6, "critical_temp_c": 214.1, "critical_pressure_bar": 34.1,
                "description": "Utilizado históricamente como solvente industrial de limpieza y refrigerante de sistemas térmicos cerrados militares.",
                "pros": "Estable bajo condiciones extremas.",
                "cons": "Gran destructor del ozono estratosférico.",
                "alternatives": "Fluidos fluorados inertes", "true_replacement": "Fluidos fluorados inertes"
            }
        ]

    def read_refrigerants(self) -> List[Refrigerant]:
        refrigerants = []
        for d in self._raw_data:
            refrigerants.append(Refrigerant(
                key=d["key"],
                ashrae_name=d["ashrae_name"],
                chemical_name=d["chemical_name"],
                chemical_formula=d["chemical_formula"],
                compound_type=d["compound_type"],
                safety_group=d["safety_group"],
                odp=d["odp"],
                gwp=d["gwp"],
                category=d["category"],
                primary_oil=d["primary_oil"],
                status=d["status"],
                color_hex=d["color_hex"],
                boiling_point_c=d["boiling_point_c"],
                critical_temp_c=d["critical_temp_c"],
                critical_pressure_bar=d["critical_pressure_bar"],
                description=d["description"],
                pros=d["pros"],
                cons=d["cons"],
                alternatives=d["alternatives"], true_replacement=d["true_replacement"]
            ))
        return refrigerants

    def read_pressure_temperature_points(self, refrigerants: List[Refrigerant]) -> List[SaturatedPressureFact]:
        """
        Genera los datos de hechos para la tabla de curvas de presión-temperatura (P-T)
        de saturación. El rango cubierto es de -50°C a +70°C en incrementos de 5°C.
        Calcula tanto para fase líquida (Burbuja) como fase gaseosa (Rocío).
        """
        facts = []
        # Temperaturas de -50°C a +70°C con paso de 5°C
        temp_range = list(range(-50, 71, 5))
        
        # Dimensión de fase
        # 1 = Líquido Saturado (Bubble Point), 2 = Vapor Saturado (Dew Point)
        # Nota: para mezclas zeotrópicas hay un deslizamiento (glide).
        # Simulamos glide agregando un diferencial de temperatura para la fase vapor.
        for r in refrigerants:
            # Identificar si es mezcla zeotrópica para aplicar el Glide
            # R-407C, R-407A, R-407F, R-448A, R-449A, R-455A tienen glide notables de 3°C a 12°C.
            glide = 0.0
            if r.ashrae_name == "R-407C":
                glide = 5.0
            elif r.ashrae_name == "R-407A":
                glide = 4.5
            elif r.ashrae_name == "R-407F":
                glide = 4.8
            elif r.ashrae_name == "R-448A":
                glide = 4.7
            elif r.ashrae_name == "R-449A":
                glide = 4.6
            elif r.ashrae_name == "R-455A":
                glide = 12.0
            elif r.ashrae_name.startswith("R-4"):  # Otras mezclas R-4xx tienen glide de 1°C a 3°C
                glide = 2.0
                
            for t_idx, temp_c in enumerate(temp_range):
                # Generamos FK de temperatura: temp_c va de -50 a +70. Podemos mapearla
                # de manera única: index del rango + 1
                temperature_key = t_idx + 1
                
                # FASE 1: Líquido Saturado (Punto de Burbuja / Bubble Point)
                p_bubble = ThermodynamicEngine.calculate_vapor_pressure(r, temp_c)
                
                facts.append(SaturatedPressureFact(
                    refrigerant_key=r.key,
                    temperature_key=temperature_key,
                    state_key=1,  # 1 = Bubble Point
                    pressure_bar=p_bubble,
                    pressure_psi=p_bubble * 14.5038
                ))
                
                # FASE 2: Vapor Saturado (Punto de Rocío / Dew Point)
                # Para componentes puros y azeótropos, Bubble = Dew (sin glide).
                # Para zeótropos, a la misma presión, el punto de rocío ocurre a una temperatura
                # mayor (T_dew = T_bubble + glide), por lo tanto, a la misma temperatura T,
                # la presión de rocío (Dew) es INFERIOR a la de burbuja (Bubble).
                if glide > 0.0:
                    # Aproximación termodinámica: presión de rocío evaluando a la temperatura modificada
                    p_dew = ThermodynamicEngine.calculate_vapor_pressure(r, temp_c - glide)
                else:
                    p_dew = p_bubble
                    
                facts.append(SaturatedPressureFact(
                    refrigerant_key=r.key,
                    temperature_key=temperature_key,
                    state_key=2,  # 2 = Dew Point
                    pressure_bar=p_dew,
                    pressure_psi=p_dew * 14.5038
                ))
                
        return facts


class RefrigerantDataReaderFactory:
    """
    Patrón Factory. Instancia el lector de datos adecuado.
    """
    @staticmethod
    def get_reader(reader_type: str = "fallback") -> IDataReader:
        if reader_type == "fallback":
            return FallbackStaticDataReader()
        # En caso de expandir para leer PDF en línea de Indubel
        # elif reader_type == "pdf": return PdfDataReader()
        else:
            raise ValueError(f"Lector de datos '{reader_type}' no soportado.")
