import h3
import pandas as pd

def _to_h3(lat, lng, resolution):
    # Compatible across both h3-py v3 (geo_to_h3) and v4 (latlng_to_cell)
    try:
        return h3.latlng_to_cell(float(lat), float(lng), int(resolution))
    except AttributeError:
        return h3.geo_to_h3(float(lat), float(lng), int(resolution))

def assign_h3(df: pd.DataFrame, lat_col: str = "latitude", lng_col: str = "longitude", resolution: int = 8) -> pd.DataFrame:
    """Projects latitude and longitude coordinates into Uber H3 hexagonal cells."""
    df = df.copy()
    # List comprehension avoids pandas DataFrame/Series assignment ValueError
    df["zone_id"] = [
        _to_h3(lat, lng, resolution)
        for lat, lng in zip(df[lat_col], df[lng_col])
    ]
    return df

def get_h3_coords(zone_id: str) -> tuple:
    """Returns the (latitude, longitude) centroid of an H3 cell."""
    try:
        return h3.cell_to_latlng(zone_id)
    except AttributeError:
        return h3.h3_to_geo(zone_id)