from pathlib import Path
import sqlite3
import json
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parents[3] / "data"

@st.cache_data
def load_kriometrics_data():
    """
    Carga de forma optimizada en caché las dimensiones y hechos de la base relacional SQLite.
    """
    db_path = DATA_DIR / "processed" / "refrigerants.db"
    if not db_path.is_file():
        st.error("Base de datos SQLite relacional no encontrada. Ejecute el ETL primero.")
        return None, None, None, None
        
    from contextlib import closing
    with closing(sqlite3.connect(db_path.as_uri() + "?mode=ro", uri=True)) as conn:
        df_ref = pd.read_sql_query("SELECT * FROM dim_refrigerant", conn)
        df_temp = pd.read_sql_query("SELECT * FROM dim_temperature", conn)
        df_state = pd.read_sql_query("SELECT * FROM dim_state", conn)
        df_facts = pd.read_sql_query("SELECT * FROM fact_pressure_temperature", conn)
    
    return df_ref, df_temp, df_state, df_facts

@st.cache_data
def load_kriometrics_images_map():
    """
    Carga en caché el archivo de mapeo del catálogo de fotos reales de cilindros.
    """
    map_path = DATA_DIR / "refrigerants_images_map.json"
    if map_path.is_file():
        with open(map_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}
