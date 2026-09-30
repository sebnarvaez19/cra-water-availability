"""Home page."""

import json
from typing import Any

import branca
import folium
import pandas as pd
import streamlit as st
from geopandas import GeoDataFrame
from shapely.geometry import Point
from streamlit_folium import st_folium

from src.utils.data import join_uhs_to_basin, load_table, load_tables


@st.cache_data
def load_watersheds() -> dict[str, GeoDataFrame]:
    """Load defined watersheds.

    Returns
    -------
    dict[str, GeoDataFrame]
        Watershed GeoDataFrames.

    """
    return load_tables(["Q_so6", "Q_so7", "Q_so8"], labels=["Orden 6", "Orden 7", "Orden 8"])


@st.cache_data
def load_uhs() -> GeoDataFrame:
    """Load the UHS basin polygons for the spatial join.

    Returns
    -------
    GeoDataFrame
        UHS GeoDataFrame.

    """
    return load_table("uhs")


@st.dialog("Cuencas de gran tamaño")
def too_big_watersheds_warning(order: str) -> None:
    """Warn users from selecting too big watersheds.

    Parameters
    ----------
    order : str
        Order to warn.

    """
    st.info(
        f"""
            Cuidado, las cuencas de {order.lower()} cuentan con una extensión muy grande,
            revisar criterios técnicos con mucho detalle.
        """,
        icon=":material/warning:",
    )


st.title("Oferta estimada departamental")
st.text("Disponibilidad hídrica y viabilidad ambiental para la construcción de reservorios de agua en el Atlántico")

selector_watershed = st.selectbox(
    label="Orden de cuenca",
    options=["Orden 6", "Orden 7", "Orden 8"],
)

watersheds = load_watersheds()
selected_watershed = watersheds[selector_watershed].copy()
selected_watershed["feature_id"] = range(len(selected_watershed))
selected_watershed = join_uhs_to_basin(selected_watershed, load_uhs())

if st.session_state.get("selected_layer") != selector_watershed:
    st.session_state["selected_layer"] = selector_watershed
    st.session_state["selected_feature_id"] = None

if st.session_state.get("selected_layer") in {"Orden 8", "Orden 7"}:
    too_big_watersheds_warning(str(st.session_state.get("selected_layer")))

selected_id = st.session_state["selected_feature_id"]

offer_series = selected_watershed["oferta_estimada_anual"].dropna() / 1000.0
min_value = float(offer_series.min())
max_value = float(offer_series.max())

colormap = branca.colormap.LinearColormap(
    colors=["#f1eef6", "#bdc9e1", "#74a9cf", "#0570b0"],
    vmin=min_value,
    vmax=max_value,
    caption="Oferta Estimada Anual (m³)",
)

center_lat = 10.6769886733
center_lon = -74.9652266742

map_obj = folium.Map(location=[center_lat, center_lon], zoom_start=10, width="100%")


def choropleth_style(feature: dict[str, dict]) -> dict[str, str | float]:
    """Style each polygon according to the annual water offer in cubic meters.

    Parameters
    ----------
    feature : Any
        Polygon to style.

    Returns
    -------
    dict[str, str | float]
        Style specification.

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


def get_clicked_feature_id(map_data: dict[str, Any] | None, watershed: GeoDataFrame) -> int | None:
    """Resolve the clicked polygon from the st_folium payload.

    Parameters
    ----------
    map_data : dict[str, Any] | None
        Value returned by ``st_folium``.
    watershed : GeoDataFrame
        Layer with a ``feature_id`` column, used when the payload has no feature properties.

    Returns
    -------
    int | None
        Clicked ``feature_id`` or None when nothing was clicked.

    """
    if not map_data:
        return None

    properties = (map_data.get("last_active_drawing") or {}).get("properties") or {}
    if properties.get("feature_id") is not None:
        return int(properties["feature_id"])

    click = map_data.get("last_object_clicked")
    if click:
        hits = watershed[watershed.contains(Point(click["lng"], click["lat"]))]
        if not hits.empty:
            return int(hits["feature_id"].iloc[0])
    return None


map_col, table_col = st.columns([65, 35])

with map_col:
    folium.GeoJson(
        json.loads(selected_watershed.to_json()),
        name=selector_watershed,
        style_function=choropleth_style,
        tooltip=None,
    ).add_to(map_obj)

    # The highlight is an overlay so selecting a polygon does not remount the map and reset zoom/pan.
    highlight = None
    if selected_id is not None:
        highlight = folium.FeatureGroup(name="Cuenca seleccionada")
        folium.GeoJson(
            json.loads(selected_watershed[selected_watershed["feature_id"] == selected_id].to_json()),
            style_function=lambda _: {"fillColor": "#dc2626", "color": "#7f1d1d", "weight": 2, "fillOpacity": 0.9},
            tooltip=None,
        ).add_to(highlight)

    map_data = st_folium(
        map_obj,
        key="watershed-map",
        use_container_width=True,
        height=400,
        feature_group_to_add=highlight,
        returned_objects=["last_object_clicked", "last_active_drawing"],
    )

    clicked_id = get_clicked_feature_id(map_data, selected_watershed)
    if clicked_id is not None and clicked_id != selected_id:
        st.session_state["selected_feature_id"] = clicked_id
        st.rerun()

    st.markdown(
        f"""
        <div style="width: 100%; max-width: 100%; margin-top: 0.5rem;">
            <div style="font-size: 0.9rem; font-weight: 600; margin-bottom: 0.3rem;">
                Oferta Estimada Anual m³
            </div>
            <div style="width: 100%; height: 12px; border-radius: 6px;
                background: linear-gradient(to right, #f1eef6 0%, #bdc9e1 33%,
                #74a9cf 66%, #0570b0 100%);"></div>
            <div style="display: flex; justify-content: space-between;
                font-size: 0.75rem; color: #444; margin-top: 0.2rem;">
                <span>{min_value:,.0f}</span>
                <span>{((min_value + max_value) / 2):,.0f}</span>
                <span>{max_value:,.0f}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with table_col:
    if selected_id is None:
        st.info("Haga clic en una cuenca del mapa para ver sus datos.")
    else:
        row = selected_watershed[selected_watershed["feature_id"] == selected_id].iloc[0]
        uhs_name = row["uhs_name"] if pd.notna(row["uhs_name"]) else "Sin dato"

        details = pd.DataFrame(
            {
                "Valor": [
                    f"{row['area_km2']:,.2f}",
                    f"{row['caudal_aprovechable_l_s']:,.2f}",
                    f"{row['oferta_estimada_anual'] / 1000.0:,.0f}",
                    row["basin_name"],
                    uhs_name,
                ],
            },
            index=[
                "Area de la cuenca (km²)",
                "Caudal aprovechable (l/s)",
                "Oferta estimada anual (m³)",
                "Subcuenca",
                "Cuenca hidrográfica",
            ],
        )

        st.dataframe(details, width="stretch")
