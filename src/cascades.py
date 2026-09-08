import pandas as pd
from typing import List, Dict

def build_cascades(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assembles chronological mobility cascades from sessions.
    Compresses consecutive check-ins in the exact same zone,
    retaining sequences with at least 2 distinct transitions/stops.
    """
    cascades: List[Dict] = []
    
    # Sort entire dataframe upfront to guarantee temporal order
    df_sorted = df.sort_values(by=["session_id", "timestamp"])
    
    for session_id, group in df_sorted.groupby("session_id"):
        if len(group) < 2:
            continue
            
        # Deduplicate consecutive identical zones
        mask = group["zone_id"].ne(group["zone_id"].shift())
        deduped = group[mask]
        
        # Keep sequences with at least 2 hops
        if len(deduped) >= 2:
            sequence = list(zip(deduped["category_group"], deduped["zone_id"]))
            cascades.append({
                "session_id": session_id,
                "sequence": sequence,
                "timestamps": list(deduped["timestamp"]),
                "length": len(sequence)
            })

    return pd.DataFrame(cascades)