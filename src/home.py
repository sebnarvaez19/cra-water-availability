"""Home page."""

import json
from typing import Any

import branca
import folium
import streamlit as st
from geopandas import GeoDataFrame
from streamlit_folium import st_folium

from src.utils.data import load_tables


@st.cache_data
def load_watersheds() -> dict[str, GeoDataFrame]:
    """Load defined watersheds.

    Returns
    -------
    dict[str, GeoDataFrame]
        Watershed GeoDataFrames.

    """
    return load_tables(["Q_so8", "Q_so7", "Q_so6"], labels=["Orden 8", "Orden 7", "Orden 6"])


st.title("Oferta estimada departamental")
st.text("Disponibilidad hídrica y viabilidad ambiental para la construcción de reservorios de agua en el Atlántico")

selector_watershed = st.selectbox(
    label="Orden de cuenca",
    options=["Orden 8", "Orden 7", "Orden 6"],
)

watersheds = load_watersheds()
selected_watershed = watersheds[selector_watershed]

offer_series = selected_watershed["oferta_estimada_anual"].dropna() / 1000.0
min_value = float(offer_series.min())
max_value = float(offer_series.max())

colormap = branca.colormap.LinearColormap(
    colors=["#f1eef6", "#bdc9e1", "#74a9cf", "#0570b0"],
    vmin=min_value,
    vmax=max_value,
    caption="Oferta total estimada anual (rendimiento 75%) m3",
)

center_lat = 10.6769886733
center_lon = -74.9652266742

map_obj = folium.Map(location=[center_lat, center_lon], zoom_start=10, width=1080)


def choropleth_style(feature: Any) -> dict[str, str | float]:
    """Style each polygon according to the annual water offer in cubic meters.

    Parameters
    ----------
    feature : Any
        spatial feature to draw.

    Returns
    -------
    dict[str, str | float]
        style sheet for feature.

    """
    value = feature["properties"].get("oferta_estimada_anual", 0)
    if value is None:
        value = 0
    value_m3 = float(value) / 1000.0
    return {
        "fillColor": colormap(value_m3),
        "color": "#1F3A5F",
        "weight": 1,
        "fillOpacity": 0.75,
    }


folium.GeoJson(
    json.loads(selected_watershed.to_json()),
    name=selector_watershed,
    style_function=choropleth_style,
).add_to(map_obj)

map_component = st_folium(map_obj, width=1080, height=600)

st.markdown(
    f"""
    <div style="width: 100%; max-width: 100%; margin-top: 0.5rem;">
        <div style="font-size: 0.9rem; font-weight: 600; margin-bottom: 0.3rem;">
            Oferta total estimada anual (rendimiento 75%) m3
        </div>
        <div style="width: 100%; height: 12px; border-radius: 6px; background: linear-gradient(to right, #f1eef6 0%, #bdc9e1 33%, #74a9cf 66%, #0570b0 100%);"></div>
        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #444; margin-top: 0.2rem;">
            <span>{min_value:,.0f}</span>
            <span>{((min_value + max_value) / 2):,.0f}</span>
            <span>{max_value:,.0f}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

_ = map_component
