from pathlib import Path
from src.config import (
    RAW_DATA_PATH, RESULTS_DIR, FIGURES_DIR,
    H3_RESOLUTION, MAX_SESSION_GAP_HOURS, MIN_SUPPORT, MIN_CONFIDENCE
)
from src.preprocessing import load_data, clean_data, classify_category, create_sessions
from src.spatial import assign_h3
from src.cascades import build_cascades
from src.mining import mine_sequential_patterns
from src.centrality import build_cascade_graph, calculate_sequential_centrality
from src.baselines import extract_zone_features, identify_hidden_hotspots
from src.visualization import export_visualizations
from src.validation import explain_zone

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Ingestion & Spatial Preprocessing
    print("[1/6] Loading and cleaning check-in data...")
    df = load_data(RAW_DATA_PATH)
    print(f"       Raw records: {len(df)}")
    
    df = clean_data(df)
    print(f"       Records after clean & NYC bounds: {len(df)}")

    df["category_group"] = df["category"].apply(classify_category)
    print(f"       Category breakdown:\n{df['category_group'].value_counts().to_string()}")

    df = create_sessions(df, max_gap_hours=MAX_SESSION_GAP_HOURS)
    print(f"       Unique sessions created: {df['session_id'].nunique()}")

    df = assign_h3(df, resolution=H3_RESOLUTION)
    print(f"       Unique H3 zones: {df['zone_id'].nunique()}")

   # 2. Extract Mobility Cascades
    print("[2/6] Building tourist mobility cascades...")
    zone_features = extract_zone_features(df)
    cascades = build_cascades(df)
    print(f"       Total cascades constructed (length >= 2): {len(cascades)}")
    
    if len(cascades) == 0:
        print("\n[!] FATAL: 0 cascades were formed. Checking sample data...")
        print(df[["user_id", "session_id", "timestamp", "zone_id"]].head(10))
        return

    # 3. Constrained Pattern Mining
    print("[3/6] Mining sequential transition patterns...")
    patterns = mine_sequential_patterns(cascades, min_support=MIN_SUPPORT, min_confidence=MIN_CONFIDENCE)
    print(f"       Mined patterns above thresholds: {len(patterns)}")

    if len(patterns) == 0:
        print("\n[!] FATAL: 0 patterns mined. Thresholds (min_support / min_confidence) are still too high, or transitions are being pruned.")
        return

    # 4. Graph Construction & Centrality Computation
    print("[4/6] Building graph and scoring Sequential Centrality...")
    G = build_cascade_graph(patterns)
    print(f"       Graph Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")

    centrality = calculate_sequential_centrality(G)
    centrality["zone_id"] = centrality["zone_id"].astype(str)
    zone_features["zone_id"] = zone_features["zone_id"].astype(str)

    final_ranking = centrality.merge(zone_features, on="zone_id", how="left")
    hidden_hotspots = identify_hidden_hotspots(final_ranking)

    # 5. Persist Results
    print("[5/6] Exporting tables and visual assets...")
    final_ranking.to_csv(RESULTS_DIR / "final_zone_ranking.csv", index=False)
    patterns.to_csv(RESULTS_DIR / "mined_sequential_patterns.csv", index=False)
    hidden_hotspots.to_csv(RESULTS_DIR / "hidden_hotspots.csv", index=False)
    export_visualizations(final_ranking, df, FIGURES_DIR)

    # 6. Terminal Summary and Interpretability Demo
    print("[6/6] Execution complete.\n")
    display_cols = ["zone_id", "sequential_centrality", "visits", "downstream_count"]
    print("Top Candidate Zones:")
    print(final_ranking[display_cols].head(10).to_string(index=False))

    if not final_ranking.empty:
        top_zone = str(final_ranking.iloc[0]["zone_id"])
        print("\nInterpretability Demo for Top Ranked Zone:")
        explain_zone(top_zone, patterns, centrality)

if __name__ == "__main__":
    main()