import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
import h3
from pathlib import Path

RESULTS_DIR = Path("results")
FIGURES_DIR = Path("figures")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# 1. Load Generated Datasets
ranking = pd.read_csv(RESULTS_DIR / "final_zone_ranking.csv")
patterns = pd.read_csv(RESULTS_DIR / "mined_sequential_patterns.csv")
hotspots = pd.read_csv(RESULTS_DIR / "hidden_hotspots.csv")

# Ensure complete coordinates for H3 cells
def resolve_coords(row):
    lat = row.get("latitude")
    lng = row.get("longitude")
    if pd.isna(lat) or pd.isna(lng):
        try:
            return h3.cell_to_latlng(str(row["zone_id"]))
        except AttributeError:
            return h3.h3_to_geo(str(row["zone_id"]))
    return lat, lng

coords = [resolve_coords(r) for _, r in ranking.iterrows()]
ranking["latitude"] = [c[0] for c in coords]
ranking["longitude"] = [c[1] for c in coords]

# 2. Output Table 1: Top Candidate Flagship Zones
print("\n" + "="*80)
print("TABLE 1: TOP 10 CANDIDATE ZONES BY SEQUENTIAL CENTRALITY")
print("="*80)
display_cols = ["zone_id", "sequential_centrality", "visits", "unique_users", "downstream_count"]
top10 = ranking[display_cols].head(10).copy()
top10["sequential_centrality"] = top10["sequential_centrality"].round(4)
print(top10.to_string(index=False))

# 3. Output Table 2: Hidden Hotspots (High Centrality vs Lower Footfall)
print("\n" + "="*80)
print("TABLE 2: TOP DISCOVERED 'HIDDEN HOTSPOTS'")
print("="*80)
hotspot_cols = ["zone_id", "sequential_centrality", "visits", "downstream_count"]
top_hotspots = hotspots[hotspot_cols].head(5).copy()
top_hotspots["sequential_centrality"] = top_hotspots["sequential_centrality"].round(4)
print(top_hotspots.to_string(index=False))

# 4. Visualization 1: Top 15 Zones Barplot
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.figure(figsize=(10, 6))
top15 = ranking.head(15).sort_values("sequential_centrality", ascending=True)
bars = plt.barh(top15["zone_id"].astype(str), top15["sequential_centrality"], color="#2b5c8f", edgecolor="black")
plt.xlabel("Sequential Centrality Score", fontsize=12, fontweight="bold")
plt.ylabel("H3 Spatial Cell (Zone ID)", fontsize=12, fontweight="bold")
plt.title("TourCascade: Top 15 Predicted Luxury Flagship Corridors", fontsize=14, fontweight="bold", pad=15)
plt.xlim(0, 1.05)
for bar in bars:
    w = bar.get_width()
    plt.text(w + 0.01, bar.get_y() + bar.get_height()/2, f"{w:.3f}", va="center", fontsize=9)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "review_top_zones_barplot.png", dpi=300)
plt.close()

# 5. Visualization 2: Footfall vs. Sequential Centrality Quadrant
plt.figure(figsize=(9, 6))
sns.scatterplot(
    data=ranking,
    x="visits",
    y="sequential_centrality",
    alpha=0.6,
    color="#4a90e2",
    s=50,
    edgecolor="none"
)

# Annotate Top Hidden Hotspots
for _, row in top_hotspots.head(3).iterrows():
    plt.scatter(row["visits"], row["sequential_centrality"], color="#d9534f", s=80, edgecolors="black")
    plt.annotate(
        f"Hidden: {row['zone_id'][:8]}...",
        (row["visits"], row["sequential_centrality"]),
        textcoords="offset points",
        xytext=(8, -4),
        fontsize=8,
        fontweight="bold",
        color="#d9534f"
    )

plt.axhline(ranking["sequential_centrality"].quantile(0.75), color="gray", linestyle="--", alpha=0.7, label="75th % Centrality")
plt.axvline(ranking["visits"].quantile(0.50), color="gray", linestyle=":", alpha=0.7, label="50th % Footfall")
plt.xlabel("Raw Footfall Volume (Total Check-ins)", fontsize=11, fontweight="bold")
plt.ylabel("Sequential Centrality Score", fontsize=11, fontweight="bold")
plt.title("Novelty Validation: Decoupling of Footfall from Sequential Demand Flow", fontsize=13, fontweight="bold", pad=12)
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "review_footfall_vs_centrality_quadrant.png", dpi=300)
plt.close()

# 6. Visualization 3: Enhanced Interactive Choropleth/Hex Map
valid_coords = ranking.dropna(subset=["latitude", "longitude"])
center = [valid_coords["latitude"].mean(), valid_coords["longitude"].mean()]
m = folium.Map(location=center, zoom_start=12, tiles="CartoDB positron")

# Color code markers based on ranking tier
for idx, row in valid_coords.head(25).iterrows():
    is_hotspot = row["zone_id"] in hotspots["zone_id"].values
    color = "#e74c3c" if is_hotspot else "#2980b9"
    popup_text = f"""
    <div style='font-family: Arial; font-size: 12px; width: 200px;'>
        <b>Zone ID:</b> {row['zone_id']}<br>
        <b>Sequential Centrality:</b> {row['sequential_centrality']:.4f}<br>
        <b>Visits:</b> {int(row['visits'])}<br>
        <b>Inflow Degree:</b> {int(row['downstream_count'])}<br>
        <b>Type:</b> {'<span style="color:red;">Hidden Hotspot</span>' if is_hotspot else 'Primary Corridor'}
    </div>
    """
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=8 if is_hotspot else 6,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.8,
        popup=folium.Popup(popup_text, max_width=250)
    ).add_to(m)

m.save(str(FIGURES_DIR / "tourcascade_interactive_review_map.html"))
print("\n[✔] Output generation complete! All assets refreshed in figures/ and results/.")