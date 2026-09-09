"""
TourCascade - Temporal Validation and Explainability
"""

import numpy as np
import pandas as pd


def chronological_split(
    df,
    test_fraction=0.30,
):
    """
    Split mobility data chronologically.

    The first (1-test_fraction) is training data.
    The final test_fraction is test data.
    """

    if df.empty:
        return df.copy(), df.copy()

    data = df.sort_values(
        "timestamp"
    ).copy()

    split_index = int(
        len(data) * (1 - test_fraction)
    )

    train = data.iloc[:split_index].copy()
    test = data.iloc[split_index:].copy()

    return train, test


def calculate_future_activity(
    test_df,
):
    """
    Calculate future activity for every zone.
    """

    if test_df.empty:
        return pd.DataFrame(
            columns=[
                "zone_id",
                "future_visits",
                "future_users",
            ]
        )

    result = (
        test_df.groupby("zone_id")
        .agg(
            future_visits=("zone_id", "size"),
            future_users=("user_id", "nunique"),
        )
        .reset_index()
    )

    result["zone_id"] = (
        result["zone_id"]
        .astype(str)
    )

    return result


def precision_at_k(
    predicted_zones,
    actual_zones,
    k,
):
    """
    Precision@K.
    """

    predicted = list(predicted_zones)[:k]
    actual = set(actual_zones)

    if not predicted:
        return 0.0

    hits = sum(
        1
        for zone in predicted
        if zone in actual
    )

    return hits / len(predicted)


def recall_at_k(
    predicted_zones,
    actual_zones,
    k,
):
    """
    Recall@K.
    """

    predicted = list(predicted_zones)[:k]
    actual = set(actual_zones)

    if not actual:
        return 0.0

    hits = sum(
        1
        for zone in predicted
        if zone in actual
    )

    return hits / len(actual)


def validate_predictions(
    ranking,
    future_activity,
    ks=(5, 10, 20),
):
    """
    Compare Sequential Centrality rankings with
    future activity.

    Actual future hotspots are defined as the top zones
    by future visit count.
    """

    if ranking.empty or future_activity.empty:
        return pd.DataFrame()

    merged = ranking.merge(
        future_activity,
        on="zone_id",
        how="left",
    )

    merged["future_visits"] = (
        merged["future_visits"]
        .fillna(0)
    )

    # Top 20% future zones as actual hotspots
    threshold = merged[
        "future_visits"
    ].quantile(0.80)

    actual_hotspots = set(
        merged.loc[
            merged["future_visits"] >= threshold,
            "zone_id",
        ]
    )

    predicted = merged.sort_values(
        "sequential_centrality",
        ascending=False,
    )["zone_id"].tolist()

    rows = []

    for k in ks:

        rows.append(
            {
                "k": k,
                "precision_at_k": precision_at_k(
                    predicted,
                    actual_hotspots,
                    k,
                ),
                "recall_at_k": recall_at_k(
                    predicted,
                    actual_hotspots,
                    k,
                ),
                "actual_hotspot_count": len(
                    actual_hotspots
                ),
            }
        )

    # Spearman-style rank correlation
    rank_data = merged[
        [
            "sequential_centrality",
            "future_visits",
        ]
    ].copy()

    rank_data["sc_rank"] = (
        rank_data["sequential_centrality"]
        .rank(
            ascending=False,
            method="average",
        )
    )

    rank_data["future_rank"] = (
        rank_data["future_visits"]
        .rank(
            ascending=False,
            method="average",
        )
    )

    correlation = (
        rank_data[
            ["sc_rank", "future_rank"]
        ]
        .corr()
        .iloc[0, 1]
    )

    for row in rows:
        row["spearman_correlation"] = correlation

    return pd.DataFrame(rows)


def explain_zone(
    zone_id,
    patterns,
    centrality=None,
    top_n=5,
):
    """
    Return the strongest sequential patterns ending
    at the selected zone.
    """

    if patterns is None or patterns.empty:
        print(
            f"No sequential patterns available for zone {zone_id}."
        )
        return

    zone_id = str(zone_id)

    candidates = patterns[
        patterns["target_zone"].astype(str)
        == zone_id
    ].copy()

    if candidates.empty:
        print(
            f"No supporting cascade found for zone {zone_id}."
        )
        return

    candidates = candidates.sort_values(
        [
            "confidence",
            "support",
        ],
        ascending=False,
    ).head(top_n)

    print(
        f"\nWhy is zone {zone_id} recommended?"
    )

    if centrality is not None:

        row = centrality[
            centrality["zone_id"].astype(str)
            == zone_id
        ]

        if not row.empty:

            score = row.iloc[0][
                "sequential_centrality"
            ]

            print(
                f"Sequential Centrality: {score:.4f}"
            )

    print("\nSupporting tourist sequences:")

    for i, (_, row) in enumerate(
        candidates.iterrows(),
        start=1,
    ):

        print(
            f"{i}. {row['pattern']}"
        )

        print(
            f"   Support: "
            f"{row['support']:.2%}"
        )

        print(
            f"   Confidence: "
            f"{row['confidence']:.2%}"
        )

    print(
        "\nInterpretation:"
    )

    print(
        "This zone repeatedly appears as a "
        "downstream destination in tourist "
        "mobility sequences."
    )