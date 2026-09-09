from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"

RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = PROJECT_ROOT / "figures"


RAW_DATA_PATH = (
    RAW_DATA_DIR
    / "dataset_TSMC2014_NYC.csv"
)


H3_RESOLUTION = 8

MAX_SESSION_GAP_HOURS = 4

MIN_SUPPORT = 0.01

MIN_CONFIDENCE = 0.20