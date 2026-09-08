import pandas as pd
from collections import defaultdict
from typing import List, Dict
from src.config import MIN_SUPPORT, MIN_CONFIDENCE

# Disallow hops from/to non-tourist background categories, but allow natural retail/food explorations
DISALLOWED_CATEGORIES = {"OTHER"}

def mine_sequential_patterns(
    cascades: pd.DataFrame,
    min_support: float = MIN_SUPPORT,
    min_confidence: float = MIN_CONFIDENCE
) -> pd.DataFrame:
    """Mines sequential transitions satisfying spatial and category transition rules."""
    total_sessions = len(cascades)
    if total_sessions == 0:
        print("Warning: Cascades DataFrame is empty.")
        return pd.DataFrame()

    edge_sessions = defaultdict(set)
    antecedent_sessions = defaultdict(set)

    for _, row in cascades.iterrows():
        seq = row["sequence"]
        session_id = row["session_id"]

        for i in range(len(seq) - 1):
            cat1, zone1 = seq[i]
            cat2, zone2 = seq[i + 1]

            # Skip self-loops within identical spatial zones
            if zone1 == zone2:
                continue

            # Drop non-commercial background noise
            if cat1 in DISALLOWED_CATEGORIES or cat2 in DISALLOWED_CATEGORIES:
                continue

            edge = (cat1, zone1, cat2, zone2)
            antecedent = (cat1, zone1)

            edge_sessions[edge].add(session_id)
            antecedent_sessions[antecedent].add(session_id)

    patterns: List[Dict] = []
    for (cat1, zone1, cat2, zone2), sessions in edge_sessions.items():
        support = len(sessions) / total_sessions
        antecedent_count = len(antecedent_sessions[(cat1, zone1)])
        confidence = len(sessions) / max(antecedent_count, 1)

        if support >= min_support and confidence >= min_confidence:
            patterns.append({
                "from_category": cat1,
                "from_zone": zone1,
                "to_category": cat2,
                "to_zone": zone2,
                "support": support,
                "confidence": confidence,
                "session_count": len(sessions)
            })

    df_patterns = pd.DataFrame(patterns)
    print(f"-> Mined {len(df_patterns)} sequential movement patterns across {total_sessions} cascades.")

    if not df_patterns.empty:
        df_patterns = df_patterns.sort_values(
            by=["confidence", "support"],
            ascending=[False, False]
        ).reset_index(drop=True)

    return df_patterns