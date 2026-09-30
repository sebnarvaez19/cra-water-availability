"""Calculate reservoir performance based on area."""

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from geopandas import GeoDataFrame

from src.utils.data import load_table, merge_loaded_tables

st.title("Calculo de oferta disponible según reservorio")
st.text("Estimación de volumen total disponible basado en caudal específico y dimensiones de la cuenca.")


@st.cache_data
def load_watersheds() -> GeoDataFrame:
    """Load defined watersheds.

    Returns
    -------
    GeoDataFrame
        Watershed GeoDataFrames.

    """
    df = merge_loaded_tables(["Q_so6", "Q_so7", "Q_so8"], labels=["Orden 6", "Orden 7", "Orden 8"])
    df["oferta_estimada_anual"] /= 1000
    return df


@st.cache_data
def load_basin() -> GeoDataFrame:
    """Load defined basins.

    Returns
    -------
    GeoDataFrame
        Basins to filter.

    """
    return load_table("watersheds")


selector_basin = st.selectbox(
    label="Seleccione una cuenca",
    options=load_basin()["name"].unique(),
)

if st.session_state.get("selected_basin") != selector_basin:
    st.session_state["selected_basin"] = selector_basin
    st.session_state["filtered_watershed"] = load_watersheds().query(f"basin_name == '{selector_basin}'")


df = st.session_state.get("filtered_watershed")
if df is not None and not df.empty:
    color_map = {
        "Orden 8": "#F1C40F",  # Yellow
        "Orden 7": "#2ECC71",  # Green
        "Orden 6": "#3498DB",  # Blue
    }

    clean_df = df.dropna(subset=["area_km2", "oferta_estimada_anual", "label"])
    fig = px.scatter(
        clean_df,
        x="area_km2",
        y="oferta_estimada_anual",
        color="label",
        color_discrete_map=color_map,
        labels={
            "area_km2": "Área (km²)",
            "oferta_estimada_anual": "Oferta Estimada Anual (m³)",
            "label": "Orden",
        },
        title="Área vs. Oferta Estimada Anual con Línea de Regresión Global",
    )

    x = clean_df["area_km2"].array
    y = clean_df["oferta_estimada_anual"].array

    if len(x) > 1:
        slope, intercept = np.polyfit(x, y, 1)
        x_trend = np.linspace(x.min(), x.max(), 100)
        y_trend = slope * x_trend + intercept

        fig.add_trace(
            go.Scatter(
                x=x_trend,
                y=y_trend,
                mode="lines",
                name="Regresión",
                line={"color": "#E74C3C", "width": 2, "dash": "dash"},
                hovertemplate="Área: %{x:.2f}<br>Oferta: %{y:.2f}",
            ),
        )

    fig.update_layout(
        template="plotly_white",
        legend_title_text="Categoría",
        hovermode="closest",
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No hay datos disponibles en `st.session_state['filtered_watershed']`.")
