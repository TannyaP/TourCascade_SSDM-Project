from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import folium
from src.spatial import get_h3_coords

def export_visualizations(
    ranking: pd.DataFrame, 
    df_raw: pd.DataFrame, 
    output_dir: Path
):
    """Outputs visual assets: bar rankings, scatter correlations, and interactive HTML map."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if ranking.empty:
        print("Warning: Ranking dataframe is empty. Skipping visualization export.")
        return

    top20 = ranking.head(20).sort_values("sequential_centrality").copy()

    # 1. Bar Chart
    plt.figure(figsize=(10, 8))
    plt.barh(top20["zone_id"].astype(str), top20["sequential_centrality"], color="#1f77b4")
    plt.xlabel("Sequential Centrality")
    plt.ylabel("H3 Zone ID")
    plt.title("Top Candidate Zones by Sequential Centrality")
    plt.tight_layout()
    plt.savefig(output_dir / "top_sequential_centrality.png", dpi=300)
    plt.close()

    # 2. Footfall vs Centrality Scatter Plot
    plt.figure(figsize=(9, 7))
    plot_df = ranking.dropna(subset=["visits", "sequential_centrality"])
    plt.scatter(plot_df["visits"], plot_df["sequential_centrality"], alpha=0.6, edgecolors="none")
    plt.xlabel("Raw Footfall (Visits)")
    plt.ylabel("Sequential Centrality")
    plt.title("Footfall vs Sequential Centrality")
    plt.tight_layout()
    plt.savefig(output_dir / "footfall_vs_centrality.png", dpi=300)
    plt.close()

    # 3. Interactive Folium Map (Sanitize coordinates)
    valid_coords_raw = df_raw.dropna(subset=["latitude", "longitude"])
    if not valid_coords_raw.empty:
        center = [valid_coords_raw["latitude"].mean(), valid_coords_raw["longitude"].mean()]
    else:
        center = [40.7580, -73.9855]  # Default to NYC Midtown center if missing

    m = folium.Map(location=center, zoom_start=11)

    for _, row in top20.iterrows():
        lat = row.get("latitude")
        lng = row.get("longitude")

        # Fallback to H3 centroid if latitude or longitude is NaN
        if pd.isna(lat) or pd.isna(lng):
            try:
                lat, lng = get_h3_coords(str(row["zone_id"]))
            except Exception:
                continue  # Skip node if coordinates cannot be resolved

        folium.CircleMarker(
            location=[float(lat), float(lng)],
            radius=7,
            popup=(
                f"<b>Zone:</b> {row['zone_id']}<br>"
                f"<b>Sequential Centrality:</b> {row['sequential_centrality']:.3f}<br>"
                f"<b>Visits:</b> {row.get('visits', 0)}<br>"
                f"<b>Downstream Inflows:</b> {row['downstream_count']}"
            ),
            color="#e41a1c",
            fill=True,
            fill_opacity=0.7
        ).add_to(m)

    m.save(str(output_dir / "tourcascade_candidate_map.html"))