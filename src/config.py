from pathlib import Path

# Base Directory Structure
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "dataset_TSMC2014_NYC.csv"
PROCESSED_DATA_PATH = BASE_DIR / "data" / "processed" / "cleaned_trajectories.csv"
RESULTS_DIR = BASE_DIR / "results"
FIGURES_DIR = BASE_DIR / "figures"

# Spatial & Temporal Parameters
H3_RESOLUTION = 8  # Approximate cell diameter ~900m (edge ~460m)
MAX_SESSION_GAP_HOURS = 12
MIN_CASCADE_LENGTH = 3

# Lower thresholds to capture fine-grained spatial trajectories
MIN_SUPPORT = 0.0005     # Requires ~5-10 occurrences rather than 1% of all citywide trips
MIN_CONFIDENCE = 0.05    # Allows downstream transitions with 5%+ probability

# Bounding Box Coordinates (NYC Default)
NYC_BOUNDS = {
    "min_lat": 40.49,
    "max_lat": 40.92,
    "min_lng": -74.27,
    "max_lng": -73.68,
}