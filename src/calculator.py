"""Calculate reservoir performance based on area."""

import streamlit as st
from geopandas import GeoDataFrame

from src.utils.data import load_tables

st.title("Calculo de oferta disponible según reservorio")
st.text("Estimación de volumen total disponible basado en caudal específico y dimensiones de la cuenca.")


@st.cache_data
def load_watersheds() -> dict[str, GeoDataFrame]:
    """Load defined watersheds.

    Returns
    -------
    dict[str, GeoDataFrame]
        Watershed GeoDataFrames.

    """
    return load_tables(["Q_so6", "Q_so7", "Q_so8"], labels=["Orden 6", "Orden 7", "Orden 8"])
