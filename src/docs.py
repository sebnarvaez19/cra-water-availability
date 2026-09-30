"""App documentation."""

import streamlit as st

st.title("Memoria técnica")
st.info(
    """
    Esta aplicación se desarrolla de manera informativa, cualquier construcción de reservorio o demás estructuras para
    la contención de agua requerirá su correspondiente evaluación técnica y operativa.
""",
    icon=":material/warning:",
)

st.markdown(
    r"""
    ## Delimitación Morfométrica y Jerarquización de Cuencas Hidrográficas

    La delimitación de las unidades de drenaje superficial se realizó a partir de un Modelo Digital de Elevación (DEM), implementando las rutinas de análisis hidrológico y procesamiento morfométrico en **SAGA GIS (v. 9.12.4)**. El flujo de trabajo contempló el acondicionamiento topográfico previo mediante el relleno y eliminación de depresiones espurias (*sink filling*), la determinación de las direcciones de flujo superficial y la acumulación de flujo consecuente. A partir de estas variables, se extrajo la red de drenaje y se efectuó su clasificación jerárquica mediante el **orden de corriente de Strahler** (*Strahler Stream Order*).

    El método topológico de **Strahler** categoriza las corrientes según su nivel de ramificación dentro de la red fluvial: los tributarios de cabecera que no reciben aportes se definen como canales de primer orden ($n = 1$); la confluencia de dos corrientes de igual orden $n$ da origen a un segmento de orden superior $n + 1$, mientras que la unión de dos corrientes de órdenes diferentes mantiene el orden del tributario de mayor magnitud. Con base en esta discretización, se definieron los puntos de desembocadura (*outlets*) y se delimitaron las cuencas aferentes correspondientes a órdenes de drenaje **6, 7 y 8**.

    Para la escala territorial y fisiográfica del Departamento del Atlántico —caracterizado por una topografía predominantemente plana a suavemente ondulada y cuencas litorales de escasa longitud de recorrido—, se adoptó el **orden 6 como la discretización óptima recomendada**. Este nivel de segmentación logra capturar adecuadamente la heterogeneidad espacial, los drenajes directos al mar Caribe y las subcuencas tributarias del río Magdalena y del canal del Dique. Por el contrario, los **órdenes 7 y 8 resultan desaconsejados para esta jurisdicción**, dado que generan una sobreagregación espacial excesiva, agrupando áreas de drenaje desproporcionadamente extensas que diluyen los contrastes hidrológicos locales e impiden una gestión representativa del balance hídrico a nivel de microcuenca.
    """
)

st.markdown(
    r"""
    ## Rendimiento Hídrico y Estimación del Caudal Ecológico

    Para estimar el rendimiento de las cuencas hidrográficas modeladas, se empleó el **caudal específico** —o rendimiento hídrico— reportado en la *Evaluación Regional del Agua (ERA, 2023)*, definido como el volumen superficial generado por unidad de área en un intervalo temporal específico ($\text{l}/(\text{s}\cdot\text{km}^2)$). A escala de unidad hidrográfica, su cálculo se basa en el balance hídrico simulado mediante el método de humedad del suelo en WEAP (integrando precipitación, evapotranspiración real e infiltración), normalizando el caudal medio superficial ($Q_{\text{medio}}$) respecto a su área de drenaje ($A$) a través de la relación $q = \frac{Q_{\text{medio}}}{A}$, lo cual permite comparar de manera homogénea cuencas de diversas dimensiones.

    Con base en este rendimiento, se determinó el **caudal ecológico** por subcuenca, entendido como el régimen de flujo indispensable para mantener la estabilidad biológica, física y funcional de los ecosistemas fluviales. En la práctica hidrológica, este caudal se gestiona como una fracción de la oferta natural con el fin de armonizar la conservación ecológica con los requerimientos consuntivos de los sectores usuarios. Para este análisis, se adoptó una reserva ecológica del **75 % del caudal medio anual**, utilizándose dicha cota como base para el cómputo de los volúmenes anuales por subcuenca.
    """
)
