"""
Módulos de Infraestructura - Exportadores de Datos (Data Exporters)
Se encarga de persistir el Modelo Estrella en archivos CSV
y en una base de datos relacional física SQLite (data/refrigerants.db).
Genera también el JSON analítico estructurado.
"""

import os
import csv
import json
import sqlite3
from typing import List, Dict, Any
from src.domain.entities import Refrigerant, TemperatureDimension, StateDimension, SaturatedPressureFact

class StarSchemaExporter:
    """
    Clase responsable de la carga (Load) y exportación del Modelo Estrella
    tanto en archivos relacionales CSV/JSON como en una base de datos SQLite física.
    """
    def __init__(self, output_dir: str, web_data_dir: str):
        self.output_dir = output_dir
        self.web_data_dir = web_data_dir
        self.db_path = os.path.join(self.output_dir, "refrigerants.db")
        
        # Asegurar existencia de directorios
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.web_data_dir, exist_ok=True)

    def export_to_sqlite(
        self,
        refrigerants: List[Refrigerant],
        temperatures: List[TemperatureDimension],
        states: List[StateDimension],
        facts: List[SaturatedPressureFact]
    ) -> None:
        """
        Exporta el Esquema Estrella relacional a una base de datos física SQLite.
        Aplica llaves primarias, llaves foráneas e integridad referencial.
        """
        print(f"[*] Creando y poblando base de datos SQLite en '{self.db_path}'...")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Deshabilitar llaves foráneas temporalmente para poder hacer drops limpios
        cursor.execute("PRAGMA foreign_keys = OFF;")
        cursor.execute("DROP TABLE IF EXISTS fact_pressure_temperature;")
        cursor.execute("DROP TABLE IF EXISTS dim_refrigerant;")
        cursor.execute("DROP TABLE IF EXISTS dim_temperature;")
        cursor.execute("DROP TABLE IF EXISTS dim_state;")
        
        # Habilitar soporte de llaves foráneas
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # 1. Crear Tabla DimRefrigerant
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_refrigerant (
            refrigerant_key INTEGER PRIMARY KEY,
            ashrae_name TEXT NOT NULL,
            chemical_name TEXT,
            chemical_formula TEXT,
            compound_type TEXT,
            safety_group TEXT,
            odp REAL,
            gwp REAL,
            category TEXT,
            primary_oil TEXT,
            status TEXT,
            color_hex TEXT,
            boiling_point_c REAL,
            critical_temp_c REAL,
            critical_pressure_bar REAL,
            description TEXT,
            pros TEXT,
            cons TEXT,
            alternatives TEXT,
            true_replacement TEXT
        );
        """)
        
        # 2. Crear Tabla DimTemperature
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_temperature (
            temperature_key INTEGER PRIMARY KEY,
            temperature_c REAL NOT NULL,
            temperature_f REAL NOT NULL
        );
        """)
        
        # 3. Crear Tabla DimState
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_state (
            state_key INTEGER PRIMARY KEY,
            state_name TEXT NOT NULL
        );
        """)
        
        # 4. Crear Tabla FactPressureTemperature
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fact_pressure_temperature (
            refrigerant_key INTEGER,
            temperature_key INTEGER,
            state_key INTEGER,
            pressure_bar REAL,
            pressure_psi REAL,
            PRIMARY KEY (refrigerant_key, temperature_key, state_key),
            FOREIGN KEY (refrigerant_key) REFERENCES dim_refrigerant(refrigerant_key),
            FOREIGN KEY (temperature_key) REFERENCES dim_temperature(temperature_key),
            FOREIGN KEY (state_key) REFERENCES dim_state(state_key)
        );
        """)
        
        # Limpiar datos previos si los hubiera
        cursor.execute("DELETE FROM fact_pressure_temperature;")
        cursor.execute("DELETE FROM dim_refrigerant;")
        cursor.execute("DELETE FROM dim_temperature;")
        cursor.execute("DELETE FROM dim_state;")
        
        # Insertar Dimensión Refrigerante
        for r in refrigerants:
            d = r.to_dict()
            cursor.execute("""
            INSERT INTO dim_refrigerant (
                refrigerant_key, ashrae_name, chemical_name, chemical_formula,
                compound_type, safety_group, odp, gwp, category, primary_oil,
                status, color_hex, boiling_point_c, critical_temp_c, critical_pressure_bar,
                description, pros, cons, alternatives, true_replacement
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                d["refrigerant_key"], d["ashrae_name"], d["chemical_name"], d["chemical_formula"],
                d["compound_type"], d["safety_group"], d["odp"], d["gwp"], d["category"], d["primary_oil"],
                d["status"], d["color_hex"], d["boiling_point_c"], d["critical_temp_c"], d["critical_pressure_bar"],
                d["description"], d["pros"], d["cons"], d["alternatives"], d["true_replacement"]
            ))

        # Insertar Dimensión Temperatura
        for t in temperatures:
            d = t.to_dict()
            cursor.execute("""
            INSERT INTO dim_temperature (temperature_key, temperature_c, temperature_f)
            VALUES (?, ?, ?);
            """, (d["temperature_key"], d["temperature_c"], d["temperature_f"]))

        # Insertar Dimensión Estado
        for s in states:
            d = s.to_dict()
            cursor.execute("""
            INSERT INTO dim_state (state_key, state_name)
            VALUES (?, ?);
            """, (d["state_key"], d["state_name"]))

        # Insertar Hechos de Presión
        for f in facts:
            d = f.to_dict()
            cursor.execute("""
            INSERT INTO fact_pressure_temperature (
                refrigerant_key, temperature_key, state_key, pressure_bar, pressure_psi
            ) VALUES (?, ?, ?, ?, ?);
            """, (d["refrigerant_key"], d["temperature_key"], d["state_key"], d["pressure_bar"], d["pressure_psi"]))
            
        conn.commit()
        conn.close()
        print(f"[*] Base de datos SQLite física creada y poblada exitosamente con {len(facts)} registros de hechos.")

    def export_to_csv(
        self,
        refrigerants: List[Refrigerant],
        temperatures: List[TemperatureDimension],
        states: List[StateDimension],
        facts: List[SaturatedPressureFact]
    ) -> None:
        """
        Exporta las tablas del Modelo Estrella a archivos CSV independientes.
        """
        # 1. Dimensión Refrigerante
        refrigerant_file = os.path.join(self.output_dir, "dim_refrigerant.csv")
        with open(refrigerant_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "refrigerant_key", "ashrae_name", "chemical_name", "chemical_formula",
                "compound_type", "safety_group", "odp", "gwp", "category",
                "primary_oil", "status", "color_hex", "boiling_point_c",
                "critical_temp_c", "critical_pressure_bar", "description",
                "pros", "cons", "alternatives", "true_replacement"
            ])
            writer.writeheader()
            for r in refrigerants:
                writer.writerow(r.to_dict())

        # 2. Dimensión Temperatura
        temp_file = os.path.join(self.output_dir, "dim_temperature.csv")
        with open(temp_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["temperature_key", "temperature_c", "temperature_f"])
            writer.writeheader()
            for t in temperatures:
                writer.writerow(t.to_dict())

        # 3. Dimensión Estado de Presión
        state_file = os.path.join(self.output_dir, "dim_state.csv")
        with open(state_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["state_key", "state_name"])
            writer.writeheader()
            for s in states:
                writer.writerow(s.to_dict())

        # 4. Tabla de Hechos Presión-Temperatura
        fact_file = os.path.join(self.output_dir, "fact_pressure_temperature.csv")
        with open(fact_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "refrigerant_key", "temperature_key", "state_key", "pressure_bar", "pressure_psi"
            ])
            writer.writeheader()
            for fact in facts:
                writer.writerow(fact.to_dict())

        print(f"[*] Modelo Estrella exportado en CSV exitosamente en '{self.output_dir}'")

    def export_consolidated_json(
        self,
        refrigerants: List[Refrigerant],
        temperatures: List[TemperatureDimension],
        states: List[StateDimension],
        facts: List[SaturatedPressureFact]
    ) -> None:
        """
        Consolida los datos del modelo estrella en un JSON estructurado jerárquicamente.
        """
        temp_map = {t.key: t.temp_c for t in temperatures}
        state_map = {s.key: s.state_name for s in states}
        
        dashboard_data = []
        for r in refrigerants:
            r_dict = r.to_dict()
            pt_points = []
            r_facts = [f for f in facts if f.refrigerant_key == r.key]
            for fact in r_facts:
                pt_points.append({
                    "temp_c": temp_map[fact.temperature_key],
                    "state": state_map[fact.state_key],
                    "p_bar": round(fact.pressure_bar, 4),
                    "p_psi": round(fact.pressure_psi, 2)
                })
            r_dict["pt_points"] = pt_points
            dashboard_data.append(r_dict)
            
        json_file = os.path.join(self.web_data_dir, "refrigerants_dashboard.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
            
        # Generar también refrigerants_dashboard_data.js para evitar bloqueos CORS locales al abrir con file://
        js_file = os.path.join(self.web_data_dir, "refrigerants_dashboard_data.js")
        with open(js_file, "w", encoding="utf-8") as f:
            f.write("window.REFRIGERANTS_DATA = ")
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
            f.write(";\n")
            
        json_history_file = os.path.join(self.output_dir, "refrigerants_dashboard.json")
        with open(json_history_file, "w", encoding="utf-8") as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)

        print(f"[*] JSON consolidado y script de datos JS (Bypass CORS) exportados exitosamente en '{self.web_data_dir}'")
