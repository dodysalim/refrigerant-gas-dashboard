import numpy as np
import pandas as pd
import streamlit as st
from src.presentation.dashboard.pt_solver import solve_pt_interpolated

def render(df_ref):
    """
    Renderiza la sección "Ciclo de Refrigeración" con el cálculo de la relación de compresión
    y el diagrama termodinámico Presión-Entalpía.
    """
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
        h_dome = np.linspace(100, 400, 100)
        p_dome = [10 ** (2 - (h - 250)**2 / 18000) for h in h_dome]
        
        # Líneas del ciclo
        cycle_h = [150, 380, 230, 150, 150]
        cycle_p = [p_low, p_high, p_high, p_low, p_low]
        
        # Intentar importar plotly
        use_plotly = True
        try:
            import plotly.graph_objects as go
        except ImportError:
            use_plotly = False
            
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
                yaxis_type="log",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Instale 'plotly' para habilitar la visualización del Diagrama del Ciclo de Compresión.")
