"""Load and process data from GeoPackage."""

from pathlib import Path

from geopandas import GeoDataFrame, read_file

GEOPACKAGE_PATH = str(Path(__file__).parents[2] / "data" / "watersheds.gpkg")


def load_table(table_name: str, geopackage_path: str = GEOPACKAGE_PATH) -> GeoDataFrame:
    """Load table of interest from GeoPackage.

    Parameters
    ----------
    table_name : str
        Table of interest name.
    geopackage_path : str, Optional
        Path to GeoPackage file.

    Returns
    -------
    GeoDataFrame
        Table of interest.

    """
    return GeoDataFrame(read_file(geopackage_path, layer=table_name).to_crs("EPSG:3857"))


def load_tables(table_names: list[str], labels: list[str] | None = None) -> dict[str, GeoDataFrame]:
    """Load a bunch of tables from the same geopackage.

    Parameters
    ----------
    table_names : list[str]
        Tables to load.
    labels : list[str], Optional
        Labels for dictionary keys.

    Returns
    -------
    dict[str, GeoDataFrame]
        Dictionary with table_names as key an GeoDataFrame as values.

    """
    if isinstance(labels, list) and all(isinstance(label, str) for label in labels) and len(labels) == len(table_names):
        return {label: load_table(tn) for (tn, label) in zip(table_names, labels, strict=True)}
    return {tn: load_table(tn) for tn in table_names}
