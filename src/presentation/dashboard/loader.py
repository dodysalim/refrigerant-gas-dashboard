import os
import sqlite3
import json
import pandas as pd
import streamlit as st

@st.cache_data
def load_kriometrics_data():
    """
    Carga de forma optimizada en caché las dimensiones y hechos de la base relacional SQLite.
    """
    db_path = os.path.join("data", "processed", "refrigerants.db")
    if not os.path.exists(db_path):
        db_path = os.path.join("..", "data", "processed", "refrigerants.db")
        
    if not os.path.exists(db_path):
        st.error("Base de datos SQLite relacional no encontrada. Ejecute el ETL primero.")
        return None, None, None, None
        
    conn = sqlite3.connect(db_path)
    df_ref = pd.read_sql_query("SELECT * FROM dim_refrigerant", conn)
    df_temp = pd.read_sql_query("SELECT * FROM dim_temperature", conn)
    df_state = pd.read_sql_query("SELECT * FROM dim_state", conn)
    df_facts = pd.read_sql_query("SELECT * FROM fact_pressure_temperature", conn)
    conn.close()
    
    return df_ref, df_temp, df_state, df_facts

@st.cache_data
def load_kriometrics_images_map():
    """
    Carga en caché el archivo de mapeo del catálogo de fotos reales de cilindros.
    """
    map_path = os.path.join("data", "refrigerants_images_map.json")
    if not os.path.exists(map_path):
        map_path = os.path.join("..", "data", "refrigerants_images_map.json")
    if os.path.exists(map_path):
        with open(map_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}
