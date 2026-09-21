"""
TourCascade - Review 3 Temporal Validation
Uses the project's preprocessing + H3 pipeline with H3 resolution 8.

Run from the project root:
    python review3_validation_h3.py
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.preprocessing import load_data, clean_data, classify_category, create_sessions
from src.spatial import assign_h3
from src.cascades import build_cascades
from src.mining import mine_sequential_patterns
from src.centrality import build_cascade_graph, calculate_sequential_centrality

try:
    from scipy.stats import kendalltau
except Exception:
    kendalltau = None

RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
RESULTS.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)

def ndcg_at_k(predicted, relevance, k):
    pred = list(predicted)[:k]
    if not pred:
        return 0.0
    gains = [float(relevance.get(z, 0)) for z in pred]
    dcg = sum(g / np.log2(i + 2) for i, g in enumerate(gains))
    ideal = sorted(relevance.values(), reverse=True)[:k]
    idcg = sum(g / np.log2(i + 2) for i, g in enumerate(ideal))
    return float(dcg / idcg) if idcg else 0.0

def main():
    print("=" * 72)
    print("TourCascade Review 3 - ACTUAL H3 TEMPORAL VALIDATION")
    print("=" * 72)

    # 1. Load and clean exactly through project preprocessing.
    raw = load_data()
    df = clean_data(raw)
    print(f"Raw records: {len(raw):,}")
    print(f"Cleaned records: {len(df):,}")

    # 2. Category grouping and H3 resolution 8.
    df["category_group"] = df["category"].apply(classify_category)
    df = assign_h3(df, resolution=8)

    # 3. Chronological 70/30 holdout.
    df = df.sort_values("timestamp").reset_index(drop=True)
    split_idx = int(len(df) * 0.70)
    train = df.iloc[:split_idx].copy()
    test = df.iloc[split_idx:].copy()

    print(f"Training records: {len(train):,}")
    print(f"Test records: {len(test):,}")
    print(f"Training end: {train['timestamp'].max()}")
    print(f"Test start:     {test['timestamp'].min()}")
    print(f"Test end:       {test['timestamp'].max()}")

    # 4. Sessionize each period using the repository's configured gap.
    train = create_sessions(train)
    test = create_sessions(test)

    # 5. Build training cascades.
    cascades_df = build_cascades(train)
    print(f"Training cascades: {len(cascades_df):,}")

    if cascades_df.empty:
        raise RuntimeError("No training cascades were produced.")

    # The repository miner ultimately operates on sequence items.
    # For zone-level centrality, use the H3 zone component of each cascade item.
    zone_sequences = []
    for seq in cascades_df["sequence"]:
        zones = [str(item[1]) if isinstance(item, (tuple, list)) and len(item) >= 2
                 else str(item) for item in seq]
        compact = []
        for z in zones:
            if not compact or z != compact[-1]:
                compact.append(z)
        if len(compact) >= 2:
            zone_sequences.append(compact)

    print(f"Usable zone cascades: {len(zone_sequences):,}")

    # 6. Mine sequential patterns using repository miner settings.
    patterns = mine_sequential_patterns(
        zone_sequences,
        min_support=0.01,
        min_confidence=0.20,
        max_pattern_length=4,
    )

    if patterns.empty:
        raise RuntimeError("No sequential patterns were mined.")

    # 7. Build sequential graph and calculate training Sequential Centrality.
    graph = build_cascade_graph(patterns)
    centrality = calculate_sequential_centrality(graph)

    if centrality.empty:
        raise RuntimeError("Sequential Centrality returned no zones.")

    centrality["zone_id"] = centrality["zone_id"].astype(str)
    centrality = centrality.sort_values(
        "sequential_centrality", ascending=False
    ).reset_index(drop=True)

    predicted = centrality["zone_id"].tolist()

    # 8. Actual future activity: H3 is assigned directly to every test record.
    future = (
        test.groupby("zone_id")
        .agg(
            future_visits=("zone_id", "size"),
            future_users=("user_id", "nunique"),
        )
        .reset_index()
    )
    future["zone_id"] = future["zone_id"].astype(str)

    # Evaluate only zones that existed in the training ranking.
    merged = centrality.merge(future, on="zone_id", how="left")
    merged["future_visits"] = merged["future_visits"].fillna(0)
    merged["future_users"] = merged["future_users"].fillna(0)

    # Future hotspot definition: top 20% of future activity among ranked zones.
    threshold = merged["future_visits"].quantile(0.80)
    actual_hotspots = set(
        merged.loc[merged["future_visits"] >= threshold, "zone_id"]
    )

    # Binary relevance for Precision/Recall and graded relevance for NDCG.
    relevance = dict(zip(merged["zone_id"], merged["future_visits"]))

    rows = []
    for k in (5, 10, 20):
        topk = predicted[:k]
        hits = sum(z in actual_hotspots for z in topk)
        precision = hits / len(topk) if topk else 0.0
        recall = hits / len(actual_hotspots) if actual_hotspots else 0.0
        ndcg = ndcg_at_k(predicted, relevance, k)
        rows.append({
            "k": k,
            "precision_at_k": precision,
            "recall_at_k": recall,
            "ndcg_at_k": ndcg,
            "hits": hits,
            "actual_hotspot_count": len(actual_hotspots),
        })

    # Kendall rank correlation between training SC and held-out future activity.
    if kendalltau is not None and len(merged) >= 2:
        tau, pvalue = kendalltau(
            merged["sequential_centrality"],
            merged["future_visits"],
        )
        tau = float(tau)
        pvalue = float(pvalue)
    else:
        tau, pvalue = np.nan, np.nan

    metrics = pd.DataFrame(rows)
    metrics["kendall_tau"] = tau
    metrics["kendall_pvalue"] = pvalue

    # Save outputs.
    metrics.to_csv(RESULTS / "review3_validation_metrics.csv", index=False)
    merged.to_csv(RESULTS / "review3_validation_zone_details.csv", index=False)
    centrality.head(20).to_csv(RESULTS / "review3_training_top20.csv", index=False)
    patterns.head(100).to_csv(RESULTS / "review3_training_patterns.csv", index=False)

    # Simple validation figure.
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8, 5))
    x = np.arange(len(metrics))
    w = 0.25
    plt.bar(x - w, metrics["precision_at_k"], width=w, label="Precision@K")
    plt.bar(x, metrics["recall_at_k"], width=w, label="Recall@K")
    plt.bar(x + w, metrics["ndcg_at_k"], width=w, label="NDCG@K")
    plt.xticks(x, [f"@{k}" for k in metrics["k"]])
    plt.ylim(0, 1)
    plt.ylabel("Score")
    plt.title("TourCascade Temporal Holdout Validation")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "review3_validation_metrics.png", dpi=300)
    plt.close()

    # Console summary ready to paste into report.
    print("\n" + "=" * 72)
    print("FINAL VALIDATION VALUES")
    print("=" * 72)
    print(metrics[[
        "k", "precision_at_k", "recall_at_k",
        "ndcg_at_k", "hits", "actual_hotspot_count"
    ]].round(4).to_string(index=False))
    print(f"\nKendall's Tau: {tau:.4f}")
    print(f"Kendall p-value: {pvalue:.4g}")
    print(f"\nRanked training zones: {len(centrality)}")
    print(f"Future hotspot count: {len(actual_hotspots)}")
    print("\nSaved:")
    print("  results/review3_validation_metrics.csv")
    print("  results/review3_validation_zone_details.csv")
    print("  results/review3_training_top20.csv")
    print("  results/review3_training_patterns.csv")
    print("  figures/review3_validation_metrics.png")
    print("\nThese are H3-resolution-8 temporal holdout results.")

if __name__ == "__main__":
    main()
