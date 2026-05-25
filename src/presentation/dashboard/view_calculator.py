import os
import numpy as np
import pandas as pd
import streamlit as st
from src.presentation.dashboard.pt_solver import solve_pt_interpolated

def render(df_ref, images_map):
    """
    Renderiza la sección "Calculadora P-T" con la ficha técnica, imágenes reales e interpolador de presión.
    """
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
        if gas_row["critical_temp_c"] - 1 <= -50:
            start_t = max(-200.0, gas_row["boiling_point_c"] - 10)
        else:
            start_t = -50.0
        temps_range = np.linspace(start_t, min(70.0, gas_row["critical_temp_c"] - 1), 100)
        pressures_bubble = [solve_pt_interpolated(gas_row, t, "Bubble") for t in temps_range]
        
        df_chart = pd.DataFrame({"Temperatura (°C)": temps_range, "Presion Burbuja (bar)": pressures_bubble})
        
        # Intentar importar plotly.graph_objects
        use_plotly = True
        try:
            import plotly.graph_objects as go
        except ImportError:
            use_plotly = False
            
        if use_plotly:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_chart["Temperatura (°C)"], y=df_chart["Presion Burbuja (bar)"], name="Líquido/Burbuja", line=dict(color=gas_row["color_hex"], width=4)))
            
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
        else:
            st.info("Instale 'plotly' para habilitar las curvas de presión interactivas.")
