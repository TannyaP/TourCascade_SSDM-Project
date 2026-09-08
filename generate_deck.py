import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_FILE = "TourCascade_Review2_Submission.pptx"
FIGURES_DIR = Path("figures")

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

NAVY = RGBColor(16, 44, 87)
ACCENT_BLUE = RGBColor(53, 101, 169)
DARK_GRAY = RGBColor(50, 50, 50)
LIGHT_BG = RGBColor(248, 249, 250)
WHITE = RGBColor(255, 255, 255)
CARD_BORDER = RGBColor(220, 224, 230)

def add_header(slide, title_text, category="CSE3068 - SEQUENTIAL AND SPATIAL DATA MINING"):
    top_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.2))
    tf = top_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_cat = tf.paragraphs[0]
    p_cat.text = category.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = ACCENT_BLUE

    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.size = Pt(24)
    p_title.font.bold = True
    p_title.font.color.rgb = NAVY
    p_title.space_before = Pt(4)

def create_card(slide, left, top, width, height, title=""):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = LIGHT_BG
    shape.line.color.rgb = CARD_BORDER
    shape.line.width = Pt(1)

    if title:
        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = NAVY

    tb_content = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.6), width - Inches(0.5), height - Inches(0.75))
    tf_content = tb_content.text_frame
    tf_content.word_wrap = True
    tf_content.margin_left = tf_content.margin_top = tf_content.margin_right = tf_content.margin_bottom = 0
    return tf_content

def add_bullet(tf, text, bold_prefix="", level=0, size=11):
    p = tf.paragraphs[0] if len(tf.paragraphs) == 1 and tf.paragraphs[0].text == "" else tf.add_paragraph()
    p.level = level
    p.space_after = Pt(6)

    if bold_prefix:
        r1 = p.add_run()
        r1.text = bold_prefix + " "
        r1.font.bold = True
        r1.font.size = Pt(size)
        r1.font.color.rgb = DARK_GRAY

    r2 = p.add_run()
    r2.text = text
    r2.font.size = Pt(size)
    r2.font.color.rgb = DARK_GRAY

blank_layout = prs.slide_layouts[6]

# -------------------------------------------------------------
# SLIDE 1: Title Slide
# -------------------------------------------------------------
s1 = prs.slides.add_slide(blank_layout)
bg = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg.fill.solid()
bg.fill.fore_color.rgb = NAVY
bg.line.fill.background()

tb = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(4.0))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "CSE3068 - SEQUENTIAL AND SPATIAL DATA MINING | DIGITAL ASSIGNMENT 2"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = RGBColor(170, 205, 255)

p = tf.add_paragraph()
p.text = "TourCascade: Sequential Spatial Mining of Tourist Mobility Cascades for Predictive Luxury Flagship Placement"
p.font.size = Pt(30)
p.font.bold = True
p.font.color.rgb = WHITE
p.space_before = Pt(14)

p = tf.add_paragraph()
p.text = "Implementation Review & Empirical Validation Report"
p.font.size = Pt(16)
p.font.color.rgb = RGBColor(220, 230, 245)
p.space_before = Pt(10)

p = tf.add_paragraph()
p.text = "Student Name: Tannya Pasricha   |   Registration No: 23MIA1130   |   Dataset: TSMC2014 NYC Check-in Corpus"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = WHITE
p.space_before = Pt(30)

# -------------------------------------------------------------
# SLIDE 2: Problem Statement & Literature Gap
# -------------------------------------------------------------
s2 = prs.slides.add_slide(blank_layout)
add_header(s2, "1. Research Motivation, Literature Gap & Core Hypothesis")

c1 = create_card(s2, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2), "Industry & Literature Gap")
add_bullet(c1, "Luxury flagship placement requires capturing high-spending tourist flow with shopping intent, not residential or commuter density.", "The Domain Problem:")
add_bullet(c1, "Commercial GIS engines (CARTO, Placer.ai) rely on static, single-point-in-time check-in counts. They treat urban space as isolated, memoryless snapshots.", "Flaw of Existing Systems:")
add_bullet(c1, "Prior academic studies on flagship placement (e.g., Venice San Marco studies) remain qualitative, lacking predictive algorithmic formulations.", "Academic Gap:")
add_bullet(c1, "Static footfall creates false positives by over-weighting crowded transit stations and central plazas where visitors exhibit zero retail intent.", "Failure of Static Volume:")

c2 = create_card(s2, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.2), "The TourCascade Hypothesis")
add_bullet(c2, "Tourists explore cities via structured temporal trajectories (e.g., Hotel -> Cultural Landmark -> Dining -> Retail Hub).", "Sequential Cascades:")
add_bullet(c2, "A zone's retail viability is determined by its sequential downstream inflow—acting as a destination sink that captures accumulated intent from upstream anchor nodes.", "The Downstream Inflow Law:")
add_bullet(c2, "Static models penalize high-value enclaves that have moderate footfall but capture intense, conversion-ready trajectory flows. Our goal is uncovering these 'Hidden Hotspots'.", "Novel Target Identification:")
add_bullet(c2, "Full explainability: Every recommended cell must provide a transparent audit trail of upstream feeder categories and confidence scores.", "Interpretability Imperative:")

# -------------------------------------------------------------
# SLIDE 3: System Architecture & Data Engineering Pipeline
# -------------------------------------------------------------
s3 = prs.slides.add_slide(blank_layout)
add_header(s3, "2. System Architecture & Trajectory Discretization")

col_w = Inches(2.7)
h = Inches(5.2)

c1 = create_card(s3, Inches(0.8), Inches(1.7), col_w, h, "A. Data Cleaning")
add_bullet(c1, "Dataset: TSMC2014 Foursquare NYC Check-ins (227,429 raw records).", "Ingestion:")
add_bullet(c1, "Parsed non-standard Foursquare timestamps ('%a %b %d %H:%M:%S +0000 %Y') into UTC datetime.", "Timestamp Standardization:")
add_bullet(c1, "Filtered within strict NYC bounds: Lat [40.5774, 40.9176], Lng [-74.15, -73.7004].", "Geographical Bounding:")
add_bullet(c1, "Deduplicated identical user check-ins occurring within the same timestamp.", "Noise Elimination:")

c2 = create_card(s3, Inches(3.75), Inches(1.7), col_w, h, "B. Spatial Discretization")
add_bullet(c2, "Projected geographic points into Uber H3 Discrete Global Hexagonal Grid.", "Hexagonal Indexing:")
add_bullet(c2, "Selected Resolution 8 (mean area: 0.737 sq km, edge length: ~461m).", "Resolution Rationale:")
add_bullet(c2, "Hexagons provide equidistant neighboring cells, avoiding the directional distortion inherent in square grids.", "Geometric Superiority:")
add_bullet(c2, "Mapped all heterogeneous venues into standardized cell indices (zone_id).", "Spatial Uniformity:")

c3 = create_card(s3, Inches(6.7), Inches(1.7), col_w, h, "C. Session Segmentation")
add_bullet(c3, "Grouped trajectories by user_id and sorted chronologically.", "User Trajectories:")
add_bullet(c3, "Applied idle threshold Delta_t <= 12 hours between consecutive check-ins.", "Session Formulation:")
add_bullet(c3, "If Delta_t > 12h, a new session_id is initialized, isolating distinct exploratory trips.", "Temporal Boundary:")
add_bullet(c3, "Compressed consecutive stays within the same H3 hex to isolate meaningful spatial transitions.", "Spatial Compression:")

c4 = create_card(s3, Inches(9.65), Inches(1.7), col_w, h, "D. Cascade Extraction")
add_bullet(c4, "Granular venue categories mapped to: HOTEL, LANDMARK, RESTAURANT, RETAIL, TRANSPORT, OTHER.", "POI Classification:")
add_bullet(c4, "Represented as ordered sequences: [(cat_1, zone_1), (cat_2, zone_2), ..., (cat_k, zone_k)].", "Sequence Structure:")
add_bullet(c4, "Filtered to keep cascades with length >= 2 hops across distinct zones.", "Trajectory Pruning:")
add_bullet(c4, "Extracted multi-stop tourist mobility cascades across NYC.", "Resulting Corpus:")

# -------------------------------------------------------------
# SLIDE 4: Mathematical Formulation & Mining Engine
# -------------------------------------------------------------
s4 = prs.slides.add_slide(blank_layout)
add_header(s4, "3. Mathematical Formulation: Pattern Mining & Sequential Centrality")

c1 = create_card(s4, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2), "Constrained Sequential Pattern Mining")
add_bullet(c1, "Mined directed transitions e = (u -> v) where u = (cat_1, zone_1) and v = (cat_2, zone_2).", "Transaction Definition:")
add_bullet(c1, "Support(u -> v) = |Sessions containing u -> v| / |Total Sessions|", "Support Formulation:")
add_bullet(c1, "Confidence(u -> v) = |Sessions containing u -> v| / |Sessions containing u|", "Confidence Formulation:")
add_bullet(c1, "Pruned background noise categories (OTHER) and self-loops (zone_1 == zone_2) to focus strictly on spatial transfers.", "Semantic Constraints:")
add_bullet(c1, "Thresholds set to Absolute Support Count >= 2 sessions and Confidence >= 5% to capture fine-grained luxury trajectory paths.", "Mining Thresholds:")

c2 = create_card(s4, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.2), "Directed Graph & Sequential Centrality (SC)")
add_bullet(c2, "Constructed directed multigraph G = (V, E), where V is the set of H3 zones, and directed edges E represent sequential transitions.", "Graph Topology:")
add_bullet(c2, "Weight W(u, v) = Support(u -> v) * Confidence(u -> v), embedding both frequency and transition reliability.", "Edge Weight Function:")
add_bullet(c2, "Weighted Downstream Inflow: I(v) = Sum_{u in In(v)} W(u, v). Quantifies accumulated trajectory capture.", "Inflow Influx Metric:")
add_bullet(c2, "Global Network PageRank: P(v) computed over transition probability matrix to evaluate overall topological authority.", "Global Authority:")
add_bullet(c2, "SC(v) = 0.7 * I_norm(v) + 0.3 * P_norm(v). Balances immediate downstream capture with systemic reach.", "Sequential Centrality Formulation:")

# -------------------------------------------------------------
# SLIDE 5: Implementation Results & Candidate Rankings
# -------------------------------------------------------------
s5 = prs.slides.add_slide(blank_layout)
add_header(s5, "4. Empirical Results: Top Predicted Luxury Flagship Zones")

c1 = create_card(s5, Inches(0.8), Inches(1.7), Inches(6.0), Inches(5.2), "Candidate Ranking Analysis")
add_bullet(c1, "The complete pipeline was executed across 227K+ records, indexing check-ins into H3 resolution 8 cells.", "Pipeline Execution:")
add_bullet(c1, "Top candidate zones cluster around Midtown Manhattan, SoHo, and the Meatpacking District, reflecting true luxury retail patterns.", "Geographic Alignment:")
add_bullet(c1, "The highest SC scores are driven by concentrated multi-hop inflows from cultural landmarks and hotel zones.", "Downstream Convergence:")
add_bullet(c1, "Zones with modest raw footfall appear among top ranks due to high transition confidence (W(u, v)).", "Decoupling Confirmed:")
add_bullet(c1, "Results exported automatically to 'results/final_zone_ranking.csv'.", "Reproducible Asset:")

# Insert Top Zones Barplot if present
bp_path = FIGURES_DIR / "review_top_zones_barplot.png"
if not bp_path.exists():
    bp_path = FIGURES_DIR / "top_sequential_centrality.png"

if bp_path.exists():
    s5.shapes.add_picture(str(bp_path), Inches(7.1), Inches(1.7), width=Inches(5.4))
else:
    c2 = create_card(s5, Inches(7.1), Inches(1.7), Inches(5.4), Inches(5.2), "Top Candidate Ranking Asset")
    add_bullet(c2, "Run 'python output.py' to generate 'figures/review_top_zones_barplot.png'.", "Visual Asset Missing:")

# -------------------------------------------------------------
# SLIDE 6: Novelty Validation - The Hidden Hotspot Phenomenon
# -------------------------------------------------------------
s6 = prs.slides.add_slide(blank_layout)
add_header(s6, "5. Novelty Demonstration: The 'Hidden Hotspot' Effect")

c1 = create_card(s6, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2), "Statistical & Theoretical Proof of Novelty")
add_bullet(c1, "Compared Sequential Centrality directly against the primary baseline: Raw Static Footfall (Visits).", "Baseline Benchmark:")
add_bullet(c1, "The scatter plot reveals weak correlation between raw visit count and Sequential Centrality.", "Empirical Decoupling:")
add_bullet(c1, "Defined as zones ranking in the 75th percentile of SC while falling into the lower 50th percentile of raw footfall.", "Hidden Hotspot Definition:")
add_bullet(c1, "Static GIS tools overpay for high-traffic commuter areas (Penn Station, Times Square) where intent to browse luxury goods is minimal.", "The Commercial Trap:")
add_bullet(c1, "Hidden hotspots capture high-intent downstream arrivals without the premium overhead of crowded transit centers.", "Strategic Advantage:")

# Insert Quadrant Scatter Plot
sp_path = FIGURES_DIR / "review_footfall_vs_centrality_quadrant.png"
if not sp_path.exists():
    sp_path = FIGURES_DIR / "footfall_vs_centrality.png"

if sp_path.exists():
    s6.shapes.add_picture(str(sp_path), Inches(6.7), Inches(1.7), width=Inches(5.8))
else:
    c2 = create_card(s6, Inches(6.7), Inches(1.7), Inches(5.8), Inches(5.2), "Quadrant Analysis Plot")
    add_bullet(c2, "Run 'python output.py' to generate 'figures/review_footfall_vs_centrality_quadrant.png'.", "Visual Asset Missing:")

# -------------------------------------------------------------
# SLIDE 7: Interpretability & Geospatial Visualization Dashboard
# -------------------------------------------------------------
s7 = prs.slides.add_slide(blank_layout)
add_header(s7, "6. Model Interpretability & Spatial Distribution Dashboard")

c1 = create_card(s7, Inches(0.8), Inches(1.7), Inches(5.8), Inches(5.2), "Explainable AI (XAI) & Interactive Visualization")
add_bullet(c1, "Unlike black-box neural networks (LSTM, GCNs), TourCascade provides an auditable behavioral justification for every recommended cell.", "Algorithmic Transparency:")
add_bullet(c1, "RESTAURANT (882a100d29fffff) -> RESTAURANT (882a100d2dfffff)\n   Support: 0.0006  |  Confidence: 0.0702 (7.02% of all visitors departing upstream Zone A transition directly into Zone B).", "Concrete Antecedent Trace:")
add_bullet(c1, "Generated Leaflet/Folium interactive map ('figures/tourcascade_interactive_review_map.html') rendering candidate H3 clusters.", "Geospatial Map Engine:")
add_bullet(c1, "Color-coded inspection: Primary Corridors (Blue) vs. Discovered Hidden Hotspots (Red) with on-click metric inspection.", "Interactive Dashboard:")
add_bullet(c1, "Provides retail executives with clear data: exactly which hotels, landmarks, and dining corridors funnel high-spending traffic into a prospective store.", "Enterprise Utility:")

c2 = create_card(s7, Inches(6.9), Inches(1.7), Inches(5.6), Inches(5.2), "Key Implementation Artifacts")
add_bullet(c2, "github.com/TannyaP/TourCascade_SSDM-Project", "Verified Codebase:")
add_bullet(c2, "Modular Python architecture across 8 standalone modules under src/ (preprocessing, spatial, cascades, mining, centrality, baselines, visualization, validation).", "Modular Design:")
add_bullet(c2, "final_zone_ranking.csv (Full ranked candidate zones with metrics).", "Data Deliverable 1:")
add_bullet(c2, "hidden_hotspots.csv (Discovered high-conversion downstream zones).", "Data Deliverable 2:")
add_bullet(c2, "mined_sequential_patterns.csv (Extracted spatial transition rules).", "Data Deliverable 3:")
add_bullet(c2, "tourcascade_interactive_review_map.html (Interactive GIS web dashboard).", "Visualization Deliverable:")

# -------------------------------------------------------------
# SLIDE 8: Review Milestones & Review 3 Roadmap
# -------------------------------------------------------------
s8 = prs.slides.add_slide(blank_layout)
add_header(s8, "7. Milestone Verification & Final Review Roadmap")

c1 = create_card(s8, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2), "Review 2 Deliverables Completed (100%)")
add_bullet(c1, "Complete Python data engineering pipeline handling 227K+ trajectories without data leakage.", "End-to-End Execution:")
add_bullet(c1, "Uber H3 resolution 8 spatial partitioning fully operational.", "Spatial Discretization:")
add_bullet(c1, "Trajectory cascade segmentation with delta_t <= 12h session thresholds.", "Trajectory Formulation:")
add_bullet(c1, "Constrained sequential pattern miner and directed multigraph construction.", "Graph & Sequence Mining:")
add_bullet(c1, "Mathematical formulation of Sequential Centrality (SC) implemented and scored.", "Novelty Metric:")
add_bullet(c1, "Identification and quadrant validation of 'Hidden Hotspots'.", "Novelty Validation:")
add_bullet(c1, "Interactive Leaflet HTML map and automated visual asset export.", "Visualization Engine:")

c2 = create_card(s8, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.2), "Review 3: Final Submission Deliverables")
add_bullet(c2, "Chronological train/test split (70% mining period, 30% prospective validation period) to evaluate future retail trajectory capture.", "Temporal Holdout Backtesting:")
add_bullet(c2, "Formal comparison against PageRank alone, Degree Centrality, and Static Apriori Co-location rules.", "Multi-Baseline Benchmarking:")
add_bullet(c2, "Kendall's Tau and NDCG metrics measuring ranking stability across temporal splits.", "Statistical Evaluation:")
add_bullet(c2, "Final 5-Page Research Paper formatted in standard IEEE two-column style including all empirical figures and references.", "5-Page IEEE Research Report:")

prs.save(OUTPUT_FILE)
print(f"\n[SUCCESS] Presentation generated: {OUTPUT_FILE}")