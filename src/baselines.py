import pandas as pd

def extract_zone_features(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates baseline zone-level visits and spatial centroids."""
    return (
        df.groupby("zone_id")
        .agg(
            visits=("user_id", "count"),
            unique_users=("user_id", "nunique"),
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean"),
            category_count=("category_group", "nunique")
        )
        .reset_index()
    )

def identify_hidden_hotspots(
    final_ranking: pd.DataFrame,
    centrality_pct_thresh: float = 0.75,
    footfall_pct_thresh: float = 0.50
) -> pd.DataFrame:
    """Identifies high-centrality zones that are undervalued by raw footfall counts."""
    df = final_ranking.copy()
    df["centrality_percentile"] = df["sequential_centrality"].rank(pct=True)
    df["footfall_percentile"] = df["visits"].rank(pct=True)

    hotspots = df[
        (df["centrality_percentile"] >= centrality_pct_thresh) &
        (df["footfall_percentile"] <= footfall_pct_thresh)
    ].sort_values(by="sequential_centrality", ascending=False)

    return hotspots.reset_index(drop=True)