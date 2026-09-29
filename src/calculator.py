"""Calculate reservoir performance based on area."""

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
    return merge_loaded_tables(["Q_so6", "Q_so7", "Q_so8"], labels=["Orden 6", "Orden 7", "Orden 8"])


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

