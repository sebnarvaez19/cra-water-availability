"""Basic app to display water availability on Atlántico."""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st

st.set_page_config(layout="wide")
css = Path("style.css").read_text(encoding="utf-8")
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

pages = st.navigation(
    [
        st.Page("src/home.py", title="Análisis departamental"),
        st.Page("src/calculator.py", title="Calculador de volumen por reservorios"),
        st.Page("src/docs.py", title="Documentación"),
    ],
    position="top",
)
pages.run()


with st.bottom:
    st.markdown("---")
    st.markdown(
        """
        <div class="footer-brand">
            <img src="/app/static/logo.svg" alt="CRA logo" />
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='footer-text'>Corporación Autónoma Regional del Atlántico</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='footer-text'>© {datetime.now(tz=ZoneInfo('America/Bogota')).year}</div>",
        unsafe_allow_html=True,
    )
