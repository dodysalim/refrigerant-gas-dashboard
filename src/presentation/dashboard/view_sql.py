import os
import sqlite3
import pandas as pd
import streamlit as st

def render(df_ref, df_facts):
    """
    Renderiza la sección "Almacén SQL Relacional" con el diagrama relacional, 
    preliminares de tablas y la consola de consultas SQL crudas.
    """
    st.title("KrioMetrics - Almacén Relacional")
    st.subheader("Consultas OLAP y exploración física de tablas relacionales")
    
    st.markdown("""
    El pipeline ETL de **KrioMetrics** estructura físicamente la base **SQLite** bajo un **Esquema Estrella**. 
    Esto divide los descriptores fijos del gas en dimensiones y las variables de presión-temperatura en la tabla de hechos.
    """)
    
    # Diagrama Relacional Dinámico SVG/Markdown de las relaciones físicas
    st.markdown("### 📊 Relaciones Físicas y Esquema de Llaves (Modelo Estrella)")
    st.markdown("""
    ```text
       DIM_TEMPERATURE                             DIM_STATE
       ┌──────────────────────┐                    ┌──────────────────────┐
       │ temperature_key [PK] │ ──┐            ┌── │ state_key [PK]       │
       │ temperature_c        │   │            │   │ state_name           │
       │ temperature_f        │   │            │   └──────────────────────┘
       └──────────────────────┘   │            │
                                  ▼            ▼
                         FACT_PRESSURE_TEMPERATURE
                         ┌────────────────────────┐
                         │ refrigerant_key   [FK] │ ──┐
                         │ temperature_key   [FK] │   │
                         │ state_key         [FK] │   │
                         │ pressure_bar           │   │
                         │ pressure_psi           │   │
                         └────────────────────────┘   │
                                                      │
                            ┌─────────────────────────┘
                            ▼
       DIM_REFRIGERANT
       ┌──────────────────────────────────────────────────────────────────┐
       │ refrigerant_key [PK] │ ashrae_name   │ chemical_name             │
       │ chemical_formula     │ compound_type │ safety_group  │ odp │ gwp │
       │ boiling_point_c      │ critical_temp │ true_replacement │ status │
       └──────────────────────────────────────────────────────────────────┘
    ```
    """)
    
    tab_dim, tab_facts = st.tabs(["Dimensión Refrigerantes (dim_refrigerant)", "Tabla de Hechos (fact_pressure_temperature)"])
    
    with tab_dim:
        st.dataframe(df_ref[[
            "refrigerant_key", "ashrae_name", "chemical_name", "chemical_formula", 
            "compound_type", "category", "gwp", "odp", "true_replacement"
        ]], use_container_width=True, hide_index=True)
        
    with tab_facts:
        st.dataframe(df_facts.head(100), use_container_width=True, hide_index=True)
        st.caption(f"Mostrando primeros 100 hechos analíticos de un total de {df_facts.shape[0]} registros en base relacional.")
        
    # SQL crudo directo
    st.markdown("### Explorador de Consultas SQL Relacionales (Cruce Dinámico)")
    sql_input = st.text_area(
        "Ingrese una consulta SQL para correr sobre refrigerants.db:",
        """SELECT 
    r.ashrae_name, 
    t.temperature_c, 
    s.state_name, 
    f.pressure_bar 
FROM fact_pressure_temperature f
JOIN dim_refrigerant r ON f.refrigerant_key = r.refrigerant_key
JOIN dim_temperature t ON f.temperature_key = t.temperature_key
JOIN dim_state s ON f.state_key = s.state_key
WHERE r.category = 'Basic' 
  AND t.temperature_c = 0.0 
  AND s.state_name = 'Saturated Liquid (Bubble Point)'
LIMIT 5;"""
    )
    
    if st.button("Correr Consulta SQL"):
        try:
            db_path = os.path.join("data", "processed", "refrigerants.db")
            if not os.path.exists(db_path):
                db_path = os.path.join("..", "data", "processed", "refrigerants.db")
            conn = sqlite3.connect(db_path)
            df_res = pd.read_sql_query(sql_input, conn)
            conn.close()
            
            st.success("[OK] Consulta ejecutada exitosamente.")
            st.dataframe(df_res, use_container_width=True)
        except Exception as e:
            st.error(f"[FALLO] Sintaxis SQL errónea o error en base de datos: {e}")
