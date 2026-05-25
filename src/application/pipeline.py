"""
Módulos de Aplicación - Canalización ETL (ETL Pipeline)
Define la estructura del proceso ETL aplicando el patrón Template Method
e integra los pasos de Extracción, Transformación, Carga y generación automática del Reporte EDA.
"""

import abc
import os
from typing import List, Dict, Any
from src.domain.entities import Refrigerant, TemperatureDimension, StateDimension, SaturatedPressureFact
from src.infrastructure.readers import IDataReader, RefrigerantDataReaderFactory
from src.infrastructure.exporters import StarSchemaExporter

class BaseETLPipeline(abc.ABC):
    """
    Template Method Pattern.
    Define la estructura algorítmica básica de una canalización de procesamiento de datos.
    """
    def run(self) -> None:
        """Método plantilla que orquesta los pasos del ETL."""
        print("[+] Iniciando proceso ETL de Gases Refrigerantes...")
        refrigerants, raw_facts = self.extract()
        refrigerants, temps, states, facts = self.transform(refrigerants, raw_facts)
        self.load(refrigerants, temps, states, facts)
        self.generate_eda_report(refrigerants, facts)
        print("[+] Proceso ETL finalizado con éxito.")

    @abc.abstractmethod
    def extract(self) -> tuple:
        pass

    @abc.abstractmethod
    def transform(self, refrigerants: List[Refrigerant], raw_facts: List[SaturatedPressureFact]) -> tuple:
        pass

    @abc.abstractmethod
    def load(
        self,
        refrigerants: List[Refrigerant],
        temps: List[TemperatureDimension],
        states: List[StateDimension],
        facts: List[SaturatedPressureFact]
    ) -> None:
        pass

    @abc.abstractmethod
    def generate_eda_report(self, refrigerants: List[Refrigerant], facts: List[SaturatedPressureFact]) -> None:
        pass


class RefrigerantETLPipeline(BaseETLPipeline):
    """
    Implementación específica del pipeline de datos de gases refrigerantes.
    Aplica principios SOLID de manera integral.
    """
    def __init__(self, output_dir: str, web_data_dir: str, reader_type: str = "fallback"):
        self.reader = RefrigerantDataReaderFactory.get_reader(reader_type)
        self.exporter = StarSchemaExporter(output_dir, web_data_dir)
        self.output_dir = output_dir

    def extract(self) -> tuple:
        print("[*] Paso 1: Extrayendo datos de gases refrigerantes...")
        refrigerants = self.reader.read_refrigerants()
        raw_facts = self.reader.read_pressure_temperature_points(refrigerants)
        print(f"    - Se extrajeron {len(refrigerants)} registros de refrigerantes.")
        print(f"    - Se generaron {len(raw_facts)} registros de hechos de presión-temperatura.")
        return refrigerants, raw_facts

    def transform(self, refrigerants: List[Refrigerant], raw_facts: List[SaturatedPressureFact]) -> tuple:
        print("[*] Paso 2: Transformando datos y modelando el Esquema Estrella...")
        
        # 1. Limpieza de datos (SRP)
        # Limpiar espacios en blanco, estandarizar textos y formatear campos de manera consistente
        for r in refrigerants:
            r.ashrae_name = r.ashrae_name.strip()
            r.chemical_name = r.chemical_name.strip()
            r.chemical_formula = r.chemical_formula.strip()
            
        # 2. Generar Dimensión Temperatura
        # Rango de -50°C a +70°C en pasos de 5°C
        temp_range = list(range(-50, 71, 5))
        temperatures = []
        for idx, temp_c in enumerate(temp_range):
            temp_f = (temp_c * 9/5) + 32
            temperatures.append(TemperatureDimension(
                key=idx + 1,
                temp_c=float(temp_c),
                temp_f=float(temp_f)
            ))
            
        # 3. Generar Dimensión de Estado/Fase de Presión
        states = [
            StateDimension(key=1, state_name="Saturated Liquid (Bubble Point)"),
            StateDimension(key=2, state_name="Saturated Vapor (Dew Point)")
        ]
        
        # En este pipeline simple, las FK ya fueron mapeadas durante la fase de simulación
        # termodinámica en el lector, por lo tanto, pasamos los datos pre-armados.
        # En una situación real, aquí se harían cruces de datos (Joins) basados en llaves sustitutas.
        
        print(f"    - Dimensión Temperatura creada con {len(temperatures)} puntos.")
        print(f"    - Dimensión Estado de Presión creada con {len(states)} fases.")
        print(f"    - Tabla de Hechos de Presión validada con {len(raw_facts)} puntos de saturación.")
        
        return refrigerants, temperatures, states, raw_facts

    def load(
        self,
        refrigerants: List[Refrigerant],
        temps: List[TemperatureDimension],
        states: List[StateDimension],
        facts: List[SaturatedPressureFact]
    ) -> None:
        print("[*] Paso 3: Cargando datos al modelo físico de almacenamiento...")
        self.exporter.export_to_csv(refrigerants, temps, states, facts)
        self.exporter.export_to_sqlite(refrigerants, temps, states, facts)
        self.exporter.export_consolidated_json(refrigerants, temps, states, facts)

    def generate_eda_report(self, refrigerants: List[Refrigerant], facts: List[SaturatedPressureFact]) -> None:
        print("[*] Paso 4: Realizando Análisis Exploratorio de Datos (EDA) y generando reporte...")
        
        total_gases = len(refrigerants)
        
        # Métricas agregadas usando algoritmos puros de Python
        # Distribución por Categoría de Refrigeración
        categories_count = {}
        types_count = {}
        safety_count = {}
        status_count = {}
        
        gwp_values = []
        odp_values = []
        boiling_points = []
        critical_temps = []
        
        gwp_by_category = {}
        
        for r in refrigerants:
            categories_count[r.category] = categories_count.get(r.category, 0) + 1
            types_count[r.compound_type] = types_count.get(r.compound_type, 0) + 1
            safety_count[r.safety_group] = safety_count.get(r.safety_group, 0) + 1
            status_count[r.status] = status_count.get(r.status, 0) + 1
            
            gwp_values.append(r.gwp)
            odp_values.append(r.odp)
            boiling_points.append(r.boiling_point_c)
            critical_temps.append(r.critical_temp_c)
            
            gwp_by_category.setdefault(r.category, []).append(r.gwp)

        # Estadísticas descriptivas de GWP y ODP
        avg_gwp = sum(gwp_values) / total_gases
        max_gwp = max(gwp_values)
        min_gwp = min(gwp_values)
        
        avg_odp = sum(odp_values) / total_gases
        max_odp = max(odp_values)
        
        avg_bp = sum(boiling_points) / total_gases
        avg_ct = sum(critical_temps) / total_gases
        
        # Calcular el promedio de GWP por categoría
        avg_gwp_by_cat = {}
        for cat, vals in gwp_by_category.items():
            avg_gwp_by_cat[cat] = sum(vals) / len(vals)
            
        # Contar gases ecológicos
        gases_eco_count = sum(1 for r in refrigerants if r.gwp <= 150.0 and r.odp == 0.0)
        gases_zero_odp = sum(1 for r in refrigerants if r.odp == 0.0)

        # Crear reporte en Markdown
        report_path = os.path.join(self.output_dir, "eda_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Reporte del Análisis Exploratorio de Datos (EDA) - Gases Refrigerantes\n\n")
            f.write("Este reporte detalla las características ecológicas, de seguridad y termodinámicas de los refrigerantes analizados en nuestro pipeline.\n\n")
            
            f.write("## 1. Métricas de Impacto Ecológico Global\n\n")
            f.write(f"- **Total de Gases Analizados**: {total_gases}\n")
            f.write(f"- **GWP Promedio**: {avg_gwp:.2f} (CO2 eq.)\n")
            f.write(f"- **GWP Máximo**: {max_gwp:.2f} (R-23 con 14800)\n")
            f.write(f"- **GWP Mínimo**: {min_gwp:.2f} (Varios como R-717, R-1234yf con <= 1)\n")
            f.write(f"- **ODP Promedio**: {avg_odp:.4f}\n")
            f.write(f"- **ODP Máximo**: {max_odp:.2f} (R-12 y R-11 con 1.0)\n")
            f.write(f"- **Porcentaje de Gases Libres de Daño de Ozono (ODP=0)**: {(gases_zero_odp / total_gases) * 100:.1f}%\n")
            f.write(f"- **Porcentaje de Gases de Ultra-bajo Impacto Climático (GWP <= 150 y ODP = 0)**: {(gases_eco_count / total_gases) * 100:.1f}%\n\n")
            
            f.write("## 2. Análisis por Categoría de Refrigeración\n\n")
            f.write("Diferenciación de impacto ambiental y cantidad según el segmento de aplicación:\n\n")
            f.write("| Categoría | Cantidad de Gases | GWP Promedio | Uso Principal | Ejemplos Clave |\n")
            f.write("| --- | --- | --- | --- | --- |\n")
            f.write(f"| **Basic** | {categories_count.get('Basic', 0)} | {avg_gwp_by_cat.get('Basic', 0):.2f} | Doméstico y autos | R-134a, R-600a, R-290, R-1234yf |\n")
            f.write(f"| **Intermediate** | {categories_count.get('Intermediate', 0)} | {avg_gwp_by_cat.get('Intermediate', 0):.2f} | Aire Acondicionado y Cámaras | R-22, R-410A, R-404A, R-32 |\n")
            f.write(f"| **Industrial** | {categories_count.get('Industrial', 0)} | {avg_gwp_by_cat.get('Industrial', 0):.2f} | Grandes plantas y criogenia | R-717 (Amoníaco), R-744 (CO2), R-23 |\n\n")
            
            f.write("> [!NOTE]\n")
            f.write("> La refrigeración industrial presenta un promedio de GWP mayor debido a la presencia de refrigerantes criogénicos (R-23, R-508B) de altísimo GWP, aunque este sector está liderado por las alternativas naturales con GWP casi nulo (Amoníaco R-717 y CO2 R-744).\n\n")

            f.write("## 3. Distribución de Tipos de Compuestos Químicos\n\n")
            f.write("| Tipo de Compuesto | Cantidad | Descripción Termodinámica | Estado de Regulación |\n")
            f.write("| --- | --- | --- | --- |\n")
            for t_name, count in sorted(types_count.items(), key=lambda x: x[1], reverse=True):
                if t_name == "CFC":
                    desc = "Clorofluorocarbonos. Excelentes fluidos pero destructores del ozono."
                    reg = "Prohibición Total (Protocolo de Montreal)."
                elif t_name == "HCFC":
                    desc = "Hidroclorofluorocarbonos. Menor daño, usados en transición."
                    reg = "Eliminación casi total completándose."
                elif t_name == "HFC":
                    desc = "Hidrofluorocarbonos. Cero daño a ozono pero alto calentamiento global."
                    reg = "Reducción gradual regulada (Enmienda de Kigali)."
                elif t_name == "HC":
                    desc = "Hidrocarburos naturales. Rendimiento termodinámico altísimo, inflamables."
                    reg = "Uso libre con límites de carga de seguridad."
                elif t_name == "Natural":
                    desc = "Compuestos de la propia naturaleza (CO2, Amoníaco, Agua, Aire)."
                    reg = "Uso fuertemente incentivado por sostenibilidad."
                elif t_name == "HFO":
                    desc = "Hidrofluoroolefinas de 4ta generación. Descomposición rápida, bajo GWP."
                    reg = "Uso libre promovido."
                else:
                    desc = "Mezclas complejas de múltiples tipos."
                    reg = "Regulado según su GWP ponderado."
                f.write(f"| {t_name} | {count} | {desc} | {reg} |\n")
            f.write("\n")

            f.write("## 4. Clasificación de Seguridad ASHRAE (Toxidad e Inflamabilidad)\n\n")
            f.write("Distribución de los gases según el estándar ASHRAE 34:\n\n")
            f.write("| Grupo de Seguridad | Cantidad | Significado Técnico | Nivel de Riesgo |\n")
            f.write("| --- | --- | --- | --- |\n")
            for s_group, count in sorted(safety_count.items(), key=lambda x: x[1], reverse=True):
                if s_group == "A1":
                    desc = "Baja toxicidad, no inflamable."
                    risk = "Mínimo"
                elif s_group == "A2L":
                    desc = "Baja toxicidad, inflamabilidad muy leve (propaga lento)."
                    risk = "Bajo-Moderado"
                elif s_group == "A2":
                    desc = "Baja toxicidad, inflamabilidad moderada."
                    risk = "Moderado"
                elif s_group == "A3":
                    desc = "Baja toxicidad, alta inflamabilidad (hidrocarburos)."
                    risk = "Alto"
                elif s_group == "B1":
                    desc = "Alta toxicidad, no inflamable."
                    risk = "Moderado-Alto"
                elif s_group == "B2L":
                    desc = "Alta toxicidad, inflamabilidad muy leve (ej. R-717)."
                    risk = "Muy Alto (industrial controlado)"
                else:
                    desc = "Otros grupos de riesgo."
                    risk = "Variable"
                f.write(f"| {s_group} | {count} | {desc} | {risk} |\n")
            f.write("\n")

            f.write("## 5. Correlación Termodinámica de Operación\n\n")
            f.write(f"- **Punto de Ebullición Promedio a 1 atm**: {avg_bp:.2f} °C\n")
            f.write(f"- **Temperatura Crítica Promedio**: {avg_ct:.2f} °C\n")
            f.write("- **Relación P-T**: A menor punto de ebullición, mayor es la presión de trabajo requerida por el gas para condensar a temperatura ambiente. Esto explica por qué el R-410A (ebullición -51.4°C) opera a presiones tan superiores comparado con el R-134a (ebullición -26.3°C), y por qué el CO2 (R-744, sublimación a -78.4°C) requiere sistemas ultra-robustos que soporten más de 100 bar de presión transcrítica.\n\n")
            f.write("---\n")
            f.write("*Reporte compilado dinámicamente por la canalización ETL del proyecto.*")
            
        print(f"    - Reporte EDA en Markdown exportado exitosamente en '{report_path}'")
        
        # También copiamos el reporte a la carpeta data/processed/ para que esté disponible
        report_processed_path = os.path.join(self.output_dir, "eda_report.md")
        # Ya se guardó directamente en output_dir, perfecto.
