import numpy as np
import pandas as pd
import streamlit as st
from src.presentation.dashboard.pt_solver import solve_pt_interpolated

def render(df_ref):
    """
    Renderiza la sección "Comparador Termodinámico" para contrastar propiedades y curvas de presión.
    """
    st.title("KrioMetrics - Comparador de Curvas de Presión")
    st.subheader("Evaluación de sustitutos ecológicos y análisis de glide side-by-side")
    
    sel_col1, sel_col2, sel_col3 = st.columns(3)
    with sel_col1:
        g1_name = st.selectbox("Refrigerante de Referencia", df_ref["ashrae_name"].tolist(), index=15) # R-22 (index 15)
    with sel_col2:
        g2_name = st.selectbox("Sustituto Opción A", df_ref["ashrae_name"].tolist(), index=18) # R-407C
    with sel_col3:
        g3_name = st.selectbox("Sustituto Opción B", df_ref["ashrae_name"].tolist(), index=24) # R-427A
        
    g1 = df_ref[df_ref["ashrae_name"] == g1_name].iloc[0]
    g2 = df_ref[df_ref["ashrae_name"] == g2_name].iloc[0]
    g3 = df_ref[df_ref["ashrae_name"] == g3_name].iloc[0]
    
    # Tabla comparativa con destaque al Sustituto Oficial
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
    
    # Intentar importar plotly
    use_plotly = True
    try:
        import plotly.graph_objects as go
    except ImportError:
        use_plotly = False
        
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
    else:
        st.info("Instale 'plotly' para habilitar los gráficos comparativos de curvas P-T.")
