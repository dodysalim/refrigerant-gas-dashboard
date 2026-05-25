"""
KrioMetrics - Plataforma Analítica de Ciencias Termodinámicas (Python & Streamlit)
Dashboard interactivo premium de Ciencia de Datos que integra un almacén SQLite,
motores de cálculo en tiempo real y gráficos dinámicos interactivos en Plotly.
"""

import os
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

# Importar los submódulos de presentación
from src.presentation.dashboard.loader import load_kriometrics_data, load_kriometrics_images_map
from src.presentation.dashboard import view_control, view_calculator, view_comparator, view_cycle, view_sql

# Cargar datos relacionales y el mapa de fotos de cilindros
df_ref, df_temp, df_state, df_facts = load_kriometrics_data()
images_map = load_kriometrics_images_map()

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
    st.sidebar.markdown("---")
    
    # Enrutamiento modular a cada pantalla correspondiente
    if app_mode == "Dashboard de Control":
        view_control.render(df_ref)
        
    elif app_mode == "Calculadora P-T":
        view_calculator.render(df_ref, images_map)
        
    elif app_mode == "Comparador Termodinámico":
        view_comparator.render(df_ref)
        
    elif app_mode == "Ciclo de Refrigeración":
        view_cycle.render(df_ref)
        
    elif app_mode == "Almacén SQL Relacional":
        view_sql.render(df_ref, df_facts)
