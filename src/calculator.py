"""Calculate reservoir performance based on area."""

import json

import folium
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from geopandas import GeoDataFrame
from streamlit_folium import st_folium

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


basin_options = list(load_basin()["name"].unique())
default_index = 0
if "selected_basin" in st.session_state and st.session_state["selected_basin"] in basin_options:
    default_index = basin_options.index(st.session_state["selected_basin"])

selector_basin = st.selectbox(
    label="Seleccione una cuenca",
    options=basin_options,
    index=default_index,
)

if st.session_state.get("selected_basin") != selector_basin or "filtered_watershed" not in st.session_state:
    st.session_state["selected_basin"] = selector_basin
    st.session_state["filtered_watershed"] = load_watersheds().query(f"basin_name == '{selector_basin}'")

selected_basin = st.session_state.get("selected_basin", selector_basin)
basins = load_basin()
selected_polygon = basins[basins["name"] == selected_basin]

center_lat = 10.6769886733
center_lon = -74.9652266742

map_obj = folium.Map(location=[center_lat, center_lon], zoom_start=10, width="100%")

if not selected_polygon.empty:
    folium.GeoJson(
        json.loads(selected_polygon.to_json()),
        name=selected_basin,
        style_function=lambda _: {
            "fillColor": "#3498DB",
            "color": "#1F3A5F",
            "weight": 2,
            "fillOpacity": 0.5,
        },
        tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["Cuenca:"]),
    ).add_to(map_obj)

    bounds = selected_polygon.total_bounds
    map_obj.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

map_col, chart_col = st.columns(2)

with map_col:
    st_folium(
        map_obj,
        key=f"basin-map-{selected_basin}",
        use_container_width=True,
        height=450,
        returned_objects=[],
    )

with chart_col:
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
