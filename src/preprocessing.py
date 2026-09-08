import pandas as pd
from pathlib import Path
from src.config import RAW_DATA_PATH, NYC_BOUNDS, MAX_SESSION_GAP_HOURS

def load_data(filepath: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Loads mobility check-in data handling TSMC2014 TSV/CSV formats."""
    cols = ["userId", "venueId", "venueCategoryId", "venueCategory", "latitude", "longitude", "timezoneOffset", "utcTimestamp"]
    try:
        df = pd.read_csv(filepath, sep="\t", header=None, names=cols, encoding="latin1")
        # Check if tab-separated read succeeded into multiple columns
        if len(df.columns) < 8 or df["latitude"].isna().all():
            df = pd.read_csv(filepath, encoding="latin1")
    except Exception:
        df = pd.read_csv(filepath, encoding="latin1")
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans trajectory points and standardizes coordinates and timestamps."""
    # Normalize column names to lowercase for robust matching
    col_map = {col: str(col).strip().lower() for col in df.columns}
    df = df.rename(columns=col_map)

    # Standardize column names
    rename_rules = {
        "userid": "user_id",
        "venueid": "venue_id",
        "venuecategory": "category",
        "utctimestamp": "timestamp",
        "lat": "latitude",
        "lon": "longitude",
        "lng": "longitude"
    }
    df = df.rename(columns=rename_rules)

    # If headerless numeric columns were loaded
    if 0 in df.columns:
        df = df.rename(columns={
            0: "user_id", 1: "venue_id", 3: "category",
            4: "latitude", 5: "longitude", 7: "timestamp"
        })

    target_cols = ["user_id", "venue_id", "category", "latitude", "longitude", "timestamp"]
    available_cols = [c for c in target_cols if c in df.columns]
    df = df[available_cols].dropna().copy()

    # Convert coordinates to numeric
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    # Robust timestamp conversion for Foursquare formats
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%a %b %d %H:%M:%S +0000 %Y", errors="coerce")
    # Fallback generic parsing if custom format fails
    if df["timestamp"].isna().all():
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)

    df = df.dropna(subset=["latitude", "longitude", "timestamp"])

    # NYC Bounding Box filter
    df = df[
        (df["latitude"] >= NYC_BOUNDS["min_lat"]) &
        (df["latitude"] <= NYC_BOUNDS["max_lat"]) &
        (df["longitude"] >= NYC_BOUNDS["min_lng"]) &
        (df["longitude"] <= NYC_BOUNDS["max_lng"])
    ]

    df = df.drop_duplicates(subset=["user_id", "venue_id", "timestamp"])
    df = df.sort_values(by=["user_id", "timestamp"]).reset_index(drop=True)
    return df

def classify_category(category: str) -> str:
    """Groups granular POI categories into high-level functional labels."""
    c = str(category).lower()
    if any(x in c for x in ["hotel", "hostel", "resort", "motel", "lodging"]):
        return "HOTEL"
    if any(x in c for x in ["museum", "monument", "landmark", "historic", "tourist", "gallery", "park", "plaza", "theater", "attraction"]):
        return "LANDMARK"
    if any(x in c for x in ["restaurant", "cafe", "coffee", "bakery", "food", "bar", "pizza", "burger", "diner"]):
        return "RESTAURANT"
    if any(x in c for x in ["shop", "store", "mall", "boutique", "clothing", "jewelry", "retail", "shopping", "market"]):
        return "RETAIL"
    if any(x in c for x in ["airport", "station", "subway", "train", "bus", "ferry"]):
        return "TRANSPORT"
    return "OTHER"

def create_sessions(df: pd.DataFrame, max_gap_hours: int = MAX_SESSION_GAP_HOURS) -> pd.DataFrame:
    """Splits trajectory chains into discrete sessions based on idle time."""
    df = df.sort_values(["user_id", "timestamp"]).reset_index(drop=True).copy()
    
    time_gap = df.groupby("user_id")["timestamp"].diff().dt.total_seconds() / 3600.0
    is_new_session = time_gap.isna() | (time_gap > max_gap_hours)
    
    df["session_number"] = is_new_session.groupby(df["user_id"]).cumsum()
    df["session_id"] = df["user_id"].astype(str) + "_s" + df["session_number"].astype(str)
    return df