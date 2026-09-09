"""
TourCascade - Baselines and Hidden Hotspot Detection
"""

import numpy as np
import pandas as pd


def extract_zone_features(df):
    """
    Calculate static zone-level features.
    """

    if df is None or df.empty:
        return pd.DataFrame(
            columns=[
                "zone_id",
                "visits",
                "unique_users",
                "unique_venues",
            ]
        )

    features = (
        df.groupby("zone_id")
        .agg(
            visits=("zone_id", "size"),
            unique_users=("user_id", "nunique"),
            unique_venues=("venue_id", "nunique"),
        )
        .reset_index()
    )

    features["zone_id"] = (
        features["zone_id"]
        .astype(str)
    )

    # Raw footfall rank
    features["footfall_rank"] = (
        features["visits"]
        .rank(
            ascending=False,
            method="min",
        )
        .astype(int)
    )

    # Normalize footfall
    minimum = features["visits"].min()
    maximum = features["visits"].max()

    if maximum == minimum:
        features["footfall_normalized"] = 1.0
    else:
        features["footfall_normalized"] = (
            (features["visits"] - minimum)
            / (maximum - minimum)
        )

    return features


def identify_hidden_hotspots(
    ranking,
    centrality_weight=0.7,
    footfall_weight=0.3,
):
    """
    Identify zones that have strong sequential importance
    despite comparatively low static footfall.

    Hidden hotspot score:

        centrality - normalized footfall

    A positive score means the zone is more important
    sequentially than its raw traffic would suggest.
    """

    if ranking is None or ranking.empty:
        return pd.DataFrame()

    result = ranking.copy()

    result["sequential_rank"] = (
        result["sequential_centrality"]
        .rank(
            ascending=False,
            method="min",
        )
        .astype(int)
    )

    # Ensure footfall normalization exists
    if "footfall_normalized" not in result.columns:

        minimum = result["visits"].min()
        maximum = result["visits"].max()

        if maximum == minimum:
            result["footfall_normalized"] = 1.0
        else:
            result["footfall_normalized"] = (
                (result["visits"] - minimum)
                / (maximum - minimum)
            )

    result["hidden_hotspot_score"] = (
        centrality_weight
        * result["sequential_centrality"]
        - footfall_weight
        * result["footfall_normalized"]
    )

    # A zone is considered hidden when:
    # - sequential centrality is above median
    # - footfall is below median
    centrality_median = result[
        "sequential_centrality"
    ].median()

    footfall_median = result[
        "visits"
    ].median()

    result["is_hidden_hotspot"] = (
        (result["sequential_centrality"] >= centrality_median)
        &
        (result["visits"] < footfall_median)
    )

    hidden = result[
        result["is_hidden_hotspot"]
    ].copy()

    hidden = hidden.sort_values(
        "hidden_hotspot_score",
        ascending=False,
    )

    return hidden.reset_index(drop=True)