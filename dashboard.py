"""
KrioMetrics - Plataforma Analítica de Ciencias Termodinámicas (Python & Streamlit)
Dashboard interactivo premium de Ciencia de Datos que integra un almacén SQLite,
motores de cálculo en tiempo real y gráficos dinámicos interactivos en Plotly.
"""

import os
import sqlite3
import math
import numpy as np
import pandas as pd
import streamlit as st

# Configuración premium de la página de Streamlit
st.set_page_config(
    page_title="KrioMetrics - Plataforma de Analítica de Refrigeración",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS avanzados para acoplar la estética "Deep Space" de KrioMetrics
st.markdown("""
<style>
    /* Estilos generales */
    .main {
        background-color: #0d0f14;
        color: #f3f4f6;
    }
    .stSidebar {
        background-color: #07090c !important;
        border-right: 1px solid rgba(43, 51, 75, 0.4) !important;
    }
    
    /* Panel de métricas personalizado */
    .krio-metric-card {
        background: rgba(20, 23, 34, 0.65);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(43, 51, 75, 0.5);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.25s ease;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
    }
    .krio-metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
    }
    .krio-metric-card.m-green::before { background-color: #2ecc71; }
    .krio-metric-card.m-red::before { background-color: #ef4444; }
    .krio-metric-card.m-blue::before { background-color: #3498db; }
    .krio-metric-card.m-purple::before { background-color: #9b59b6; }
    
    .krio-metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(74, 87, 126, 0.8);
    }
    .krio-metric-value {
        font-size: 2.3rem;
        font-weight: 800;
        color: #f3f4f6;
        font-family: 'Outfit', sans-serif;
        line-height: 1.1;
        letter-spacing: -1px;
    }
    .krio-metric-label {
        font-size: 0.8rem;
        color: #9ca3af;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 0.4rem;
    }
    .krio-metric-sub {
        font-size: 0.75rem;
        margin-top: 0.3rem;
        font-weight: 500;
    }
    .text-green { color: #2ecc71; }
    .text-red { color: #ef4444; }
    .text-blue { color: #3498db; }
    .text-purple { color: #9b59b6; }
    .text-warning { color: #f59e0b; }
    
    /* Ficha de gas */
    .krio-summary-card {
        background-color: #141722;
        border: 1px solid rgba(43, 51, 75, 0.5);
        border-radius: 12px;
        padding: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- CARGA DE DATOS DESDE EL ALMACÉN SQLITE ---
@st.cache_data
def load_kriometrics_data():
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

df_ref, df_temp, df_state, df_facts = load_kriometrics_data()

import json

@st.cache_data
def load_kriometrics_images_map():
    map_path = os.path.join("data", "refrigerants_images_map.json")
    if os.path.exists(map_path):
        with open(map_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

images_map = load_kriometrics_images_map()

# --- VERIFICACIÓN DE PLOTLY INTERACTIVO ---
use_plotly = True
try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    use_plotly = False

if df_ref is not None:
    # --- MENÚ LATERAL (SIDEBAR) ---
    st.sidebar.markdown(
        "<div style='text-align: center; padding: 1rem 0;'>"
        "<h1 style='color:#00e1d9; margin:0; font-size:2.2rem; font-family:Outfit;'>Krio<span style='color:white;'>Metrics</span></h1>"
        "<p style='color:#6b7280; font-size:0.75rem; margin:0;'>Plataforma Termodinámica Analítica</p>"
        "</div>", 
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---")
    
    app_mode = st.sidebar.radio(
        "Navegación del Proyecto",
        ["Dashboard de Control", "Calculadora P-T", "Comparador Termodinámico", "Ciclo de Refrigeración", "Almacén SQL Relacional"]
    )
    
    # --- SOLVER TERMODINÁMICO AUXILIAR ---
    def solve_pt_interpolated(gas_row, temp_c, state_type="Bubble"):
        T = temp_c + 273.15
        T_b = gas_row["boiling_point_c"] + 273.15
        T_c = gas_row["critical_temp_c"] + 273.15
        P_c = gas_row["critical_pressure_bar"]
        
        if temp_c >= gas_row["critical_temp_c"]:
            return P_c
            
        glide = 0.0
        if state_type == "Dew":
            if gas_row["ashrae_name"] == "R-407C": glide = 5.0
            elif gas_row["ashrae_name"] == "R-455A": glide = 12.0
            elif gas_row["ashrae_name"].startswith("R-4"): glide = 2.0
            
        evaluated_temp = temp_c - glide
        T_eval = evaluated_temp + 273.15
        
        trouton = 10.5
        if gas_row["compound_type"] == "Natural":
            trouton = 12.8 if gas_row["ashrae_name"] == "R-717" else 10.6
            
        ln_p = math.log(1.01325) + trouton * T_b * (1.0 / T_b - 1.0 / T_eval)
        p_abs = math.exp(ln_p)
        
        T_r = T_eval / T_c
        if T_r > 0.6:
            correction = 1.0 + 0.15 * math.sin(math.pi * (T_r - 0.6) / 0.4)
            p_abs = p_abs * correction
            
        return min(max(p_abs, 0.005), P_c)

    # ==========================================================================
    # MODULO 1: DASHBOARD DE CONTROL GENERAL
    # ==========================================================================
    if app_mode == "Dashboard de Control":
        st.title("KrioMetrics - Dashboard de Control")
        st.subheader("Monitoreo y exploración científica sobre 55 gases refrigerantes")
        
        # Filtros de datos en el sidebar
        st.sidebar.markdown("### Filtros de Datos")
        search_query = st.sidebar.text_input("Buscador de Gases", "", placeholder="Escribe R-134a, R-717, fórmula...")
        
        categories = ["Todos"] + list(df_ref["category"].unique())
        selected_cat = st.sidebar.selectbox("Categoría de Refrigeración", categories)
        
        compounds = ["Todos"] + list(df_ref["compound_type"].unique())
        selected_comp = st.sidebar.selectbox("Tipo de Compuesto", compounds)
        
        gwp_limit = st.sidebar.slider("GWP (PCG) Máximo", 0, 15000, 15000, 100)
        bp_limit = st.sidebar.slider("Punto de Ebullición Máximo (°C)", -200, 100, 100, 5)
        
        # Filtrado de Datos
        df_filtered = df_ref.copy()
        if search_query:
            df_filtered = df_filtered[
                df_filtered["ashrae_name"].str.contains(search_query, case=False) |
                df_filtered["chemical_name"].str.contains(search_query, case=False) |
                df_filtered["chemical_formula"].str.contains(search_query, case=False)
            ]
        if selected_cat != "Todos":
            df_filtered = df_filtered[df_filtered["category"] == selected_cat]
        if selected_comp != "Todos":
            df_filtered = df_filtered[df_filtered["compound_type"] == selected_comp]
            
        df_filtered = df_filtered[(df_filtered["gwp"] <= gwp_limit) & (df_filtered["boiling_point_c"] <= bp_limit)]
        
        # Fila de métricas premium
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class='krio-metric-card m-green'>
                <div class='krio-metric-label'>Gases Coincidentes</div>
                <div class='krio-metric-value'>{df_filtered.shape[0]}</div>
                <div class='krio-metric-sub text-green'>De catálogo de {df_ref.shape[0]} gases</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            avg_gwp = df_filtered["gwp"].mean() if not df_filtered.empty else 0
            st.markdown(f"""
            <div class='krio-metric-card m-red'>
                <div class='krio-metric-label'>GWP Promedio</div>
                <div class='krio-metric-value'>{avg_gwp:.1f}</div>
                <div class='krio-metric-sub text-red'>CO2 eq. promedio</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            pct_zero_odp = (df_filtered[df_filtered["odp"] == 0].shape[0] / df_filtered.shape[0] * 100) if not df_filtered.empty else 0
            st.markdown(f"""
            <div class='krio-metric-card m-blue'>
                <div class='krio-metric-label'>Libres de Ozono</div>
                <div class='krio-metric-value'>{pct_zero_odp:.1f}%</div>
                <div class='krio-metric-sub text-blue'>ODP = 0 (Seguridad Ozono)</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            natural_count = df_filtered[df_filtered["compound_type"] == "Natural"].shape[0]
            st.markdown(f"""
            <div class='krio-metric-card m-purple'>
                <div class='krio-metric-label'>Fluidos Naturales</div>
                <div class='krio-metric-value'>{natural_count}</div>
                <div class='krio-metric-sub text-purple'>CO2, NH3, Agua, Aire</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Tabla interactiva
        st.markdown("### Tabla Científica de Especificaciones")
        st.dataframe(
            df_filtered[[
                "ashrae_name", "chemical_name", "chemical_formula", "compound_type", 
                "category", "gwp", "odp", "safety_group", "boiling_point_c", 
                "critical_temp_c", "primary_oil", "true_replacement", "status"
            ]],
            use_container_width=True,
            hide_index=True
        )
        
        # Gráficos Interactivos Premium
        st.markdown("### Análisis Gráfico Interactivo")
        gcol1, gcol2 = st.columns(2)
        
        with gcol1:
            if use_plotly:
                # Plotly Scatter Plot: Ebullición vs T. Crítica
                fig = px.scatter(
                    df_filtered,
                    x="boiling_point_c",
                    y="critical_temp_c",
                    color="category",
                    color_discrete_map={"Basic": "#2ecc71", "Intermediate": "#3498db", "Industrial": "#9b59b6"},
                    hover_name="ashrae_name",
                    hover_data=["chemical_name", "chemical_formula", "gwp", "safety_group", "true_replacement"],
                    title="Dominio Termodinámico: Pto. Ebullición vs Temp. Crítica",
                    labels={"boiling_point_c": "Punto de Ebullición (°C)", "critical_temp_c": "Temperatura Crítica (°C)"}
                )
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#0d0f14",
                    plot_bgcolor="#141722",
                    font_family="Inter",
                    title_font_family="Outfit",
                    title_font_size=16,
                    title_font_color="#00e1d9"
                )
                st.plotly_chart(fig, use_container_width=True)
                
        with gcol2:
            if use_plotly:
                # Agrupar tipos para limpiar el Pie chart (evitar amontonamiento de leyendas)
                df_comp_counts = df_filtered["compound_type"].value_counts().reset_index()
                df_comp_counts.columns = ["compound_type", "count"]
                
                # Agrupar los tipos de compuesto pequeños en "Otros HFCs/CFCs"
                threshold = 3
                large_compounds = df_comp_counts[df_comp_counts["count"] >= threshold]
                small_compounds = df_comp_counts[df_comp_counts["count"] < threshold]
                
                if not small_compounds.empty:
                    others_row = pd.DataFrame([{"compound_type": "Otros compuestos", "count": small_compounds["count"].sum()}])
                    df_pie_clean = pd.concat([large_compounds, others_row], ignore_index=True)
                else:
                    df_pie_clean = df_comp_counts
                
                fig = px.pie(
                    df_pie_clean,
                    values="count",
                    names="compound_type",
                    hole=0.5,
                    title="Distribución de Compuestos Químicos",
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#0d0f14",
                    font_family="Inter",
                    title_font_family="Outfit",
                    title_font_size=16,
                    title_font_color="#00e1d9"
                )
                st.plotly_chart(fig, use_container_width=True)

    # ==========================================================================
    # MODULO 2: CALCULADORA P-T
    # ==========================================================================
    elif app_mode == "Calculadora P-T":
        st.title("KrioMetrics - Calculadora Termodinámica P-T")
        st.subheader("Cálculos analíticos de presiones de saturación y deslizamiento térmico")
        
        cccol1, cccol2 = st.columns([1, 2])
        
        with cccol1:
            selected_gas_name = st.selectbox("Seleccione el Refrigerante", df_ref["ashrae_name"].tolist())
            gas_row = df_ref[df_ref["ashrae_name"] == selected_gas_name].iloc[0]
            
            temp_c = st.slider("Temperatura de Saturación (°C)", -50.0, 70.0, 5.0, 0.5)
            
            # Ficha detallada del gas con destaque especial al Sustituto Oficial
            st.markdown(f"""
            <div class='krio-summary-card'>
                <h4 style='color:#00e1d9; margin-top:0; font-family:Outfit;'>Ficha Técnica: {gas_row["ashrae_name"]}</h4>
                <p style='background-color:rgba(0, 225, 217, 0.15); border:1px solid #00e1d9; padding:0.6rem; border-radius:8px; font-size:0.85rem;'>
                    <strong>🔄 Sustituto Oficial Recomendado:</strong><br>
                    <span style='color:#00e1d9; font-weight:bold;'>{gas_row["true_replacement"]}</span>
                </p>
                <p><strong>Nombre Químico:</strong> {gas_row["chemical_name"]}</p>
                <p><strong>Fórmula:</strong> {gas_row["chemical_formula"]}</p>
                <p><strong>Estatus Regulador:</strong> {gas_row["status"]}</p>
                <hr style='border-color:rgba(43, 51, 75, 0.5);'>
                <p><strong>Ebullición (1 atm):</strong> {gas_row["boiling_point_c"]} °C</p>
                <p><strong>Temp. Crítica:</strong> {gas_row["critical_temp_c"]} °C</p>
                <p><strong>Presión Crítica:</strong> {gas_row["critical_pressure_bar"]} bar abs</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Mostrar imagen del cilindro del gas con el catálogo real clasificado
            ashrae_name = gas_row["ashrae_name"]
            img_path = None
            
            # Primero intentar obtener la foto real del catálogo clasificado
            if images_map and ashrae_name in images_map:
                img_path = images_map[ashrae_name]["streamlit"]
                
            # Si no está en el mapa de fotos específicas o el archivo no existe, usar el mapeo cromático general
            if not img_path or not os.path.exists(img_path):
                name_upper = ashrae_name.upper()
                comp_type = gas_row["compound_type"].upper()
                img_path = os.path.join("images", "r134a.png") # Default R-134a celeste

                if name_upper in ["R-134A", "R-513A", "R-450A"]:
                    img_path = os.path.join("images", "r134a.png")
                elif name_upper in ["R-22", "R-408A", "R-409A", "R-417A", "R-437A"]:
                    img_path = os.path.join("images", "r22.png")
                elif name_upper in ["R-290", "R-600A", "R-1270", "R-600", "R-1150"] or comp_type == "HC":
                    img_path = os.path.join("images", "r290.png")
                elif name_upper in ["R-404A", "R-422D", "R-422A", "R-438A"]:
                    img_path = os.path.join("images", "r404a.png")
                elif name_upper in ["R-410A", "R-410B", "R-32"]:
                    img_path = os.path.join("images", "r410a.png")
                elif name_upper in ["R-507", "R-507A", "R-508B", "R-23"]:
                    img_path = os.path.join("images", "r507.png")
                elif name_upper in ["R-717", "R-729", "R-718"]:
                    img_path = os.path.join("images", "r717.png")
                elif name_upper in ["R-407C", "R-407A", "R-407F", "R-427A", "R-424A"]:
                    img_path = os.path.join("images", "r407c.png")
                elif name_upper == "R-744":
                    img_path = os.path.join("images", "r744.png")
                elif name_upper in ["R-12", "R-11", "R-113", "R-114", "R-115", "R-502"] or comp_type == "CFC":
                    img_path = os.path.join("images", "r12.png")
                elif name_upper.startswith("R-1234") or name_upper.startswith("R-1233") or comp_type == "HFO" or name_upper in ["R-515B", "R-454C", "R-455A", "R-454B"]:
                    img_path = os.path.join("images", "r1234yf.png")
                else:
                    # Fallback inteligente según propiedades termodinámicas
                    if gas_row["boiling_point_c"] < -40:
                        img_path = os.path.join("images", "r404a.png")
                    elif gas_row["gwp"] > 3000:
                        img_path = os.path.join("images", "r407c.png")
                    else:
                        img_path = os.path.join("images", "r134a.png")
                
            if img_path and os.path.exists(img_path):
                st.image(img_path, caption=f"Foto de Catálogo Real - {gas_row['ashrae_name']}", use_container_width=True)
            
        with cccol2:
            st.markdown("### Valores de Operación de Saturación")
            
            if temp_c >= gas_row["critical_temp_c"]:
                st.warning(f"⚠️ **ESTADO SUPERCRÍTICO**: La temperatura seleccionada ({temp_c}°C) es superior a la temperatura crítica de este gas ({gas_row['critical_temp_c']}°C). El refrigerante es un fluido súper crítico y no existe cambio de fase.")
            else:
                p_bubble = solve_pt_interpolated(gas_row, temp_c, "Bubble")
                p_dew = solve_pt_interpolated(gas_row, temp_c, "Dew")
                
                # Glide
                glide = 0.0
                if gas_row["ashrae_name"] == "R-407C": glide = 5.0
                elif gas_row["ashrae_name"] == "R-455A": glide = 12.0
                elif gas_row["ashrae_name"].startswith("R-4"): glide = 2.0
                
                p_bubble_gauge = max(0.0, p_bubble - 1.01325)
                p_dew_gauge = max(0.0, p_dew - 1.01325)
                
                rcol1, rcol2 = st.columns(2)
                with rcol1:
                    st.markdown(f"""
                    <div style='background-color:#07090c; padding:1.5rem; border-radius:12px; border-left:5px solid #2ecc71; border:1px solid rgba(43,51,75,0.4);'>
                        <h5 style='color:#2ecc71; margin-top:0;'>Líquido Saturado (Bubble Point)</h5>
                        <p style='color:#9ca3af; font-size:0.75rem; margin:0;'>Presión manométrica de ebullición:</p>
                        <p style='margin:8px 0 0 0;'><strong style='font-size:2.2rem; color:white; font-family:Outfit;'>{p_bubble_gauge:.2f}</strong> barg</p>
                        <p style='margin:0; font-size:0.85rem; color:#9ca3af;'>{(p_bubble_gauge * 14.5038):.1f} psig</p>
                        <p style='margin:5px 0 0 0; font-size:0.75rem; color:#6b7280;'>Abs: {p_bubble:.2f} bara / {(p_bubble * 14.5038):.1f} psia</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with rcol2:
                    if glide > 0:
                        st.markdown(f"""
                        <div style='background-color:#07090c; padding:1.5rem; border-radius:12px; border-left:5px solid #00e1d9; border:1px solid rgba(43,51,75,0.4);'>
                            <h5 style='color:#00e1d9; margin-top:0;'>Vapor Saturado (Dew Point)</h5>
                            <p style='color:#9ca3af; font-size:0.75rem; margin:0;'>Presión manométrica de condensación:</p>
                            <p style='margin:8px 0 0 0;'><strong style='font-size:2.2rem; color:white; font-family:Outfit;'>{p_dew_gauge:.2f}</strong> barg</p>
                            <p style='margin:0; font-size:0.85rem; color:#9ca3af;'>{(p_dew_gauge * 14.5038):.1f} psig</p>
                            <p style='margin:5px 0 0 0; font-size:0.75rem; color:#6b7280;'>Abs: {p_dew:.2f} bara / {(p_dew * 14.5038):.1f} psia</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='background-color:#07090c; padding:1.5rem; border-radius:12px; border:1px solid rgba(43,51,75,0.4); border-left:5px solid #6b7280;'>
                            <h5 style='color:#9ca3af; margin-top:0;'>Puro / Azeótropo (No glide)</h5>
                            <p style='color:#6b7280; font-size:0.75rem; margin:0;'>Comportamiento de fase simple:</p>
                            <p style='margin:8px 0 0 0;'><strong style='font-size:2.2rem; color:white; font-family:Outfit;'>{p_bubble_gauge:.2f}</strong> barg</p>
                            <p style='margin:0; font-size:0.85rem; color:#6b7280;'>Bubble = Dew</p>
                            <p style='margin:5px 0 0 0; font-size:0.75rem; color:#6b7280;'>Abs: {p_bubble:.2f} bara / {(p_bubble * 14.5038):.1f} psia</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
            # Curva gráfica interactiva
            # Si la temperatura crítica es muy baja (ej. R-729 Aire con -140.5), adaptamos el rango de graficación
            if gas_row["critical_temp_c"] - 1 <= -50:
                start_t = max(-200.0, gas_row["boiling_point_c"] - 10)
            else:
                start_t = -50.0
            temps_range = np.linspace(start_t, min(70.0, gas_row["critical_temp_c"] - 1), 100)
            pressures_bubble = [solve_pt_interpolated(gas_row, t, "Bubble") for t in temps_range]
            
            df_chart = pd.DataFrame({"Temperatura (°C)": temps_range, "Presion Burbuja (bar)": pressures_bubble})
            
            if use_plotly:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_chart["Temperatura (°C)"], y=df_chart["Presion Burbuja (bar)"], name="Líquido/Burbuja", line=dict(color=gas_row["color_hex"], width=4)))
                
                # Dew line if glide
                if glide > 0:
                    pressures_dew = [solve_pt_interpolated(gas_row, t, "Dew") for t in temps_range]
                    fig.add_trace(go.Scatter(x=temps_range, y=pressures_dew, name="Vapor/Rocío (Dew)", line=dict(color="#00e1d9", width=3, dash='dash')))
                    
                if temp_c < gas_row["critical_temp_c"]:
                    fig.add_trace(go.Scatter(x=[temp_c], y=[solve_pt_interpolated(gas_row, temp_c, "Bubble")], name="Punto de Trabajo", mode="markers", marker=dict(color="red", size=14, line=dict(color="white", width=2))))
                    
                fig.update_layout(
                    title=f"Curva Termodinámica de Presión-Temperatura de Saturación ({gas_row['ashrae_name']})",
                    template="plotly_dark",
                    paper_bgcolor="#0d0f14",
                    plot_bgcolor="#141722",
                    font_family="Inter",
                    title_font_family="Outfit",
                    title_font_size=16,
                    title_font_color="#00e1d9",
                    xaxis_title="Temperatura (°C)",
                    yaxis_title="Presión Absoluta (bar)"
                )
                st.plotly_chart(fig, use_container_width=True)

    # ==========================================================================
    # MODULO 3: COMPARADOR TERMODINÁMICO DE REEMPLAZOS
    # ==========================================================================
    elif app_mode == "Comparador Termodinámico":
        st.title("KrioMetrics - Comparador de Curvas de Presión")
        st.subheader("Evaluación de sustitutos ecológicos y análisis de glide side-by-side")
        
        sel_col1, sel_col2, sel_col3 = st.columns(3)
        with sel_col1:
            g1_name = st.selectbox("Refrigerante de Referencia", df_ref["ashrae_name"].tolist(), index=15) # R-22 (index 15 en la lista ordenada de base)
        with sel_col2:
            g2_name = st.selectbox("Sustituto Opción A", df_ref["ashrae_name"].tolist(), index=18) # R-407C
        with sel_col3:
            g3_name = st.selectbox("Sustituto Opción B", df_ref["ashrae_name"].tolist(), index=24) # R-427A
            
        g1 = df_ref[df_ref["ashrae_name"] == g1_name].iloc[0]
        g2 = df_ref[df_ref["ashrae_name"] == g2_name].iloc[0]
        g3 = df_ref[df_ref["ashrae_name"] == g3_name].iloc[0]
        
        # Tabla comparativa con Destaque al Sustituto Oficial
        st.markdown("### Tabla Comparativa de Propiedades Clave")
        df_comp_table = pd.DataFrame({
            "Propiedad": ["Fórmula", "Compuesto", "Sustituto Oficial Recomendado", "GWP (PCG)", "ODP (PAO)", "Grupo Seguridad", "Pto. Ebullición", "Temp. Crítica", "Aceite Recomendado"],
            g1_name: [g1["chemical_formula"], g1["compound_type"], g1["true_replacement"], int(g1["gwp"]), g1["odp"], g1["safety_group"], f"{g1['boiling_point_c']} °C", f"{g1['critical_temp_c']} °C", g1["primary_oil"]],
            g2_name: [g2["chemical_formula"], g2["compound_type"], g2["true_replacement"], int(g2["gwp"]), g2["odp"], g2["safety_group"], f"{g2['boiling_point_c']} °C", f"{g2['critical_temp_c']} °C", g2["primary_oil"]],
            g3_name: [g3["chemical_formula"], g3["compound_type"], g3["true_replacement"], int(g3["gwp"]), g3["odp"], g3["safety_group"], f"{g3['boiling_point_c']} °C", f"{g3['critical_temp_c']} °C", g3["primary_oil"]]
        })
        st.dataframe(df_comp_table, use_container_width=True, hide_index=True)
        
        # Curvas superpuestas
        st.markdown("### Gráfico de Superposición P-T")
        temps_eval = np.arange(-50, 71, 5)
        
        p1 = [solve_pt_interpolated(g1, t, "Bubble") for t in temps_eval]
        p2 = [solve_pt_interpolated(g2, t, "Bubble") for t in temps_eval]
        p3 = [solve_pt_interpolated(g3, t, "Bubble") for t in temps_eval]
        
        if use_plotly:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=temps_eval, y=p1, name=g1_name, line=dict(color=g1["color_hex"], width=3.5)))
            fig.add_trace(go.Scatter(x=temps_eval, y=p2, name=g2_name, line=dict(color=g2["color_hex"], width=2.5, dash='dash')))
            fig.add_trace(go.Scatter(x=temps_eval, y=p3, name=g3_name, line=dict(color=g3["color_hex"], width=2.5, dash='dot')))
            
            fig.update_layout(
                title="Superposición de Curvas de Presión de Burbuja",
                template="plotly_dark",
                paper_bgcolor="#0d0f14",
                plot_bgcolor="#141722",
                font_family="Inter",
                title_font_family="Outfit",
                title_font_size=16,
                title_font_color="#00e1d9",
                xaxis_title="Temperatura (°C)",
                yaxis_title="Presión Absoluta (bar)"
            )
            st.plotly_chart(fig, use_container_width=True)

    # ==========================================================================
    # MODULO 4: CICLO DE REFRIGERACIÓN
    # ==========================================================================
    elif app_mode == "Ciclo de Refrigeración":
        st.title("KrioMetrics - Simulador de Ciclo Físico de Compresión")
        st.subheader("Simulación interactiva de presiones y relación de compresión recomendada")
        
        cycol1, cycol2 = st.columns([1, 2])
        
        with cycol1:
            gas_sel_name = st.selectbox("Seleccione el Gas en Circulación", df_ref["ashrae_name"].tolist())
            gas = df_ref[df_ref["ashrae_name"] == gas_sel_name].iloc[0]
            
            evap_t = st.slider("Temperatura de Evaporación (Baja) (°C)", -50.0, 10.0, -15.0, 1.0)
            cond_t = st.slider("Temperatura de Condensación (Alta) (°C)", 20.0, 70.0, 35.0, 1.0)
            
            p_low = solve_pt_interpolated(gas, evap_t, "Bubble")
            p_high = solve_pt_interpolated(gas, cond_t, "Bubble")
            
            ratio = p_high / p_low if p_low > 0 else 1.0
            
            p_low_gauge = max(0.0, p_low - 1.01325)
            p_high_gauge = max(0.0, p_high - 1.01325)
            
            st.markdown(f"""
            <div style='background-color:#141722; padding:1.5rem; border-radius:12px; border:1px solid rgba(43, 51, 75, 0.5);'>
                <h4 style='color:#00e1d9; margin-top:0; font-family:Outfit;'>Monitoreo de Ciclo de Compresión</h4>
                <p style='background-color:rgba(0, 225, 217, 0.15); border:1px solid #00e1d9; padding:0.6rem; border-radius:8px; font-size:0.85rem; margin-bottom:1rem;'>
                    <strong>🔄 Sustituto Recomendado del Fluido:</strong><br>
                    <span style='color:#00e1d9; font-weight:bold;'>{gas["true_replacement"]}</span>
                </p>
                <p><strong>Presión Succión (Baja):</strong> {p_low_gauge:.2f} barg ({(p_low_gauge*14.5038):.1f} psig) <span style='color:#6b7280; font-size:0.8rem;'>[Abs: {p_low:.2f} bara]</span></p>
                <p><strong>Presión Descarga (Alta):</strong> {p_high_gauge:.2f} barg ({(p_high_gauge*14.5038):.1f} psig) <span style='color:#6b7280; font-size:0.8rem;'>[Abs: {p_high:.2f} bara]</span></p>
                <hr style='border-color:rgba(43, 51, 75, 0.5);'>
                <h5 style='margin:0 0 5px 0;'>Relación de Compresión (P_alta / P_baja):</h5>
                <strong style='font-size:2.2rem; color:{"#ef4444" if ratio > 6.0 else "#2ecc71"}; font-family:Outfit;'>{ratio:.2f}</strong>
                <p style='font-size:0.75rem; color:#9ca3af; margin-top:5px; line-height:1.4;'>
                    {"⚠️ Relación elevada. Supera el límite recomendado de 6.0. Alto riesgo de sobrecalentamiento del bobinado del motor del compresor." if ratio > 6.0 else "✓ Relación eficiente. Rango de compresión termodinámica seguro que optimiza el COP (coeficiente de rendimiento)."}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        with cycol2:
            st.markdown("### Diagrama Conceptual del Ciclo (Presión vs Entalpía)")
            
            # Dibujar domo de saturación conceptual interactivo en Plotly
            # Usando logaritmo para la presión para asegurar que fluidos de alta presión no rompan el gráfico
            h_dome = np.linspace(100, 400, 100)
            # Un domo de presión con escala logarítmica suave
            p_dome = [10 ** (2 - (h - 250)**2 / 18000) for h in h_dome]
            
            # Líneas del ciclo
            cycle_h = [150, 380, 230, 150, 150]
            cycle_p = [p_low, p_high, p_high, p_low, p_low]
            
            if use_plotly:
                fig = go.Figure()
                # Graficar Domo
                fig.add_trace(go.Scatter(x=h_dome, y=p_dome, name="Límite Sólido/Líquido/Vapor", line=dict(color="rgba(156,163,175,0.4)", width=2, dash='dot')))
                # Graficar Ciclo de Refrigeración real
                fig.add_trace(go.Scatter(x=cycle_h, y=cycle_p, name="Proceso del Ciclo", line=dict(color="#00e1d9", width=4)))
                # Agregar puntos críticos numerados
                fig.add_trace(go.Scatter(
                    x=cycle_h[:-1], y=cycle_p[:-1], 
                    mode="markers+text", 
                    text=["1: Succión Vapor", "2: Descarga Caliente", "3: Condensado Líquido", "4: Expansión Mezcla"],
                    textposition="top center",
                    marker=dict(color="#ef4444", size=12, line=dict(color="white", width=2)),
                    name="Puntos Críticos"
                ))
                
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#0d0f14",
                    plot_bgcolor="#141722",
                    font_family="Inter",
                    title_font_family="Outfit",
                    title_font_size=15,
                    title_font_color="#00e1d9",
                    xaxis_title="Entalpía Conceptual (kJ/kg)",
                    yaxis_title="Presión de Operación (bar abs, escala Log)",
                    yaxis_type="log", # EJE LOGARÍTMICO PERFECTO PARA TODAS LAS PRESIONES
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)

    # ==========================================================================
    # MODULO 5: MODELO ESTRELLA SQL RELACIONAL
    # ==========================================================================
    elif app_mode == "Almacén SQL Relacional":
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
