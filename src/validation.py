import pandas as pd

def explain_zone(zone_id: str, patterns: pd.DataFrame, centrality: pd.DataFrame):
    """Outputs an interpretable justification for a recommended zone."""
    zone_patterns = patterns[patterns["to_zone"] == zone_id].sort_values(
        by=["confidence", "support"],
        ascending=[False, False]
    )

    score_match = centrality[centrality["zone_id"] == zone_id]
    if score_match.empty:
        print(f"Zone {zone_id} not found.")
        return

    score = score_match.iloc[0]

    print("=" * 60)
    print(f"RECOMMENDATION EXPLANATION: {zone_id}")
    print(f"Sequential Centrality:       {score['sequential_centrality']:.4f}")
    print(f"Weighted Downstream Inflow:  {score['weighted_inflow']:.4f}")
    print(f"Downstream Inflow Count:     {int(score['downstream_count'])}")
    print("\nTop Inflow Trajectory Paths:")
    
    for _, row in zone_patterns.head(5).iterrows():
        print(f"  {row['from_category']} ({row['from_zone']}) -> {row['to_category']} ({row['to_zone']})")
        print(f"    Support: {row['support']:.4f} | Confidence: {row['confidence']:.4f}")
    print("=" * 60)