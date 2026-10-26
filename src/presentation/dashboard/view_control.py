import pandas as pd
import streamlit as st

def render(df_ref):
    """
    Renderiza la sección "Dashboard de Control" con métricas, filtros y gráficos de Plotly.
    """
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
            <div class='krio-metric-label'>Gases Analizados</div>
            <div class='krio-metric-value'>{df_filtered.shape[0]}</div>
            <div class='krio-metric-sub text-green'>De catálogo de {df_ref.shape[0]} gases</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        avg_gwp = df_filtered["gwp"].mean() if not df_filtered.empty else 0
        st.markdown(f"""
        <div class='krio-metric-card m-red'>
            <div class='krio-metric-label'>GWP Promedio</div>
            <div class='krio-metric-value'>{int(round(avg_gwp)):,}</div>
            <div class='krio-metric-sub text-warning'>Reduciendo bajo Enmienda Kigali</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        pct_zero_odp = (df_filtered[df_filtered["odp"] == 0].shape[0] / df_filtered.shape[0] * 100) if not df_filtered.empty else 0
        st.markdown(f"""
        <div class='krio-metric-card m-blue'>
            <div class='krio-metric-label'>Seguridad de Ozono (ODP = 0)</div>
            <div class='krio-metric-value'>{pct_zero_odp:.1f}%</div>
            <div class='krio-metric-sub text-green'>Libres de Cloro destructivo</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        natural_count = df_filtered[df_filtered["compound_type"] == "Natural"].shape[0]
        st.markdown(f"""
        <div class='krio-metric-card m-purple'>
            <div class='krio-metric-label'>Refrigerantes Naturales</div>
            <div class='krio-metric-value'>{natural_count}</div>
            <div class='krio-metric-sub text-green'>GWP = 0-6 (Sostenibles)</div>
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
    
    # Intentar importar plotly.express
    use_plotly = True
    try:
        import plotly.express as px
    except ImportError:
        use_plotly = False
        
    if use_plotly:
        with gcol1:
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
            # Agrupar tipos para limpiar el Pie chart
            df_comp_counts = df_filtered["compound_type"].value_counts().reset_index()
            df_comp_counts.columns = ["compound_type", "count"]
            
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
    else:
        st.info("Instale 'plotly' para habilitar los gráficos interactivos.")
