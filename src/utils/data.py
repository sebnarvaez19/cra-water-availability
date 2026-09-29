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
    return GeoDataFrame(read_file(geopackage_path, layer=table_name).to_crs("EPSG:4326"))


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


def join_uhs_to_basin(data: GeoDataFrame, uhs: GeoDataFrame, basin_col: str = "basin") -> GeoDataFrame:
    """Spatially join UHS records to basin polygons and name the matched basin.

    Parameters
    ----------
    data : GeoDataFrame
        Input features to enrich with UHS basin names.
    uhs : GeoDataFrame
        UHS polygons that contain the basin names.
    basin_col : str, default "basin"
        Column in the UHS table that stores the basin name.

    Returns
    -------
    GeoDataFrame
        Data with a new ``uhs_name`` column.

    """
    data_reproj = data.to_crs("EPSG:4326") if data.crs is not None and data.crs != "EPSG:4326" else data.copy()
    uhs_reproj = uhs.to_crs("EPSG:4326") if uhs.crs is not None and uhs.crs != "EPSG:4326" else uhs.copy()

    # Representative points give one UHS per polygon; an intersects join duplicates polygons on UHS borders.
    points = GeoDataFrame(geometry=data_reproj.geometry.representative_point(), crs=data_reproj.crs)
    matched = points.sjoin(uhs_reproj[["geometry", basin_col]], how="left", predicate="within")
    matched = matched[~matched.index.duplicated(keep="first")]

    return GeoDataFrame(data_reproj.assign(uhs_name=matched[basin_col]))
