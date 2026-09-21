# 🛍️ TourCascade

### Sequential Spatial Mining of Tourist Mobility Cascades for Predictive Luxury Flagship Placement

<p align="center">
  <b>Mining tourist movement sequences to identify spatial zones with potential for future luxury retail placement.</b>
</p>

---

## 📌 Overview

**TourCascade** is a **Sequential Spatial Data Mining (SSDM)** project that studies tourist mobility patterns to identify spatial zones that may have potential for **future luxury flagship placement**.

The key idea is that tourist behaviour is not simply a collection of independent visits. Tourists typically move through destinations in sequences:

```text
Hotel → Landmark → Shopping Area → Restaurant → Next Landmark
```

A zone that repeatedly appears as a **downstream destination** in these tourist movement sequences may have strategic importance even if its current visitor count is not exceptionally high.

TourCascade therefore moves beyond static footfall analysis by combining:

* Spatial representation
* Temporal tourist mobility
* Sequential pattern mining
* Tourist movement cascades
* Sequential Centrality
* Temporal validation
* Explainable recommendations

The project's proposed research direction is to determine whether these sequential spatial patterns can help identify **future luxury retail hotspots**.

---

# 🎯 Problem Statement

Luxury flagship stores depend significantly on tourist spending, particularly in major tourism and retail destinations.

However, conventional location-selection approaches often treat a location as a **static snapshot**, relying on factors such as:

* Footfall
* Demographics
* Existing retail activity
* Point-in-time location characteristics

This misses an important aspect of tourist behaviour:

> **Tourists move through cities in sequences.**

For example:

```text
Hotel District
      ↓
Landmark
      ↓
Shopping Zone
      ↓
Restaurant
```

A zone may therefore become strategically important because it repeatedly appears as a **next stop** in tourist journeys, even if its individual footfall is relatively moderate.

The project addresses the following research gap:

> **There is a need for a computational method that mines the sequential spatial patterns of tourist movement to identify zones with potential to become future luxury retail hotspots, while also explaining why a zone was recommended.**

---

# 💡 Proposed Solution

TourCascade represents a city as a **spatial graph**.

### Nodes

Each node represents a spatial zone created using a hexagonal spatial grid.

Zones can contain tourism-relevant points of interest such as:

* Hotels
* Landmarks
* Luxury retail
* Restaurants

### Edges

Directed edges represent tourist movement between zones.

```text
       Hotel
         │
         ▼
      Landmark
         │
         ▼
   Shopping Zone
         │
         ▼
     Restaurant
```

The resulting movement sequences are mined to discover recurring **tourist mobility cascades**.

---

# ⭐ Key Research Contribution — Sequential Centrality

The central concept of TourCascade is **Sequential Centrality**.

Traditional location analysis may ask:

```text
How many tourists visit this zone?
```

TourCascade additionally asks:

```text
How frequently does this zone appear
as a downstream destination in
important tourist movement sequences?
```

For example:

```text
Hotel A → Landmark B → Zone X

Hotel C → Landmark D → Zone X

Hotel E → Restaurant F → Zone X
```

If **Zone X** repeatedly appears as a downstream destination, it may have high sequential importance.

### Conceptually:

```text
Tourist Mobility
       ↓
Sequential Patterns
       ↓
Downstream Destinations
       ↓
Sequential Centrality
       ↓
Candidate Zone Ranking
```

Sequential Centrality is therefore intended to capture an aspect of location importance that cannot be represented by raw visitor counts alone.

---

# 🔬 Methodology

## 1. Data Collection & Preprocessing

Tourist mobility observations contain information such as:

* Timestamp
* Geographic location
* Activity / check-in
* POI category

Relevant POI categories include:

```text
Hotel
Landmark
Luxury Retail
Restaurant
```

The project also considers known luxury-store locations and their opening dates as potential future ground truth for validating the predictive placement objective.

---

## 2. Spatial Representation

The city is divided into spatial zones using a **hexagonal grid**.

The project uses **H3** for spatial indexing and zone construction.

This allows individual geographic observations to be converted into consistent spatial units.

```text
        ⬡   ⬡   ⬡
      ⬡   ⬡   ⬡   ⬡
        ⬡   ⬡   ⬡
      ⬡   ⬡   ⬡   ⬡
```

Each zone can then be associated with relevant POIs and tourist activity.

---

## 3. Sequential Cascade Mining

Tourist observations are ordered temporally to construct movement sequences.

Example:

```text
Tourist 1:
Hotel → Landmark → Retail

Tourist 2:
Hotel → Restaurant → Retail

Tourist 3:
Hotel → Landmark → Restaurant → Retail
```

TourCascade uses **PrefixSpan as the foundation for sequential pattern mining**, with spatial and category constraints applied to the mining process.

The resulting patterns represent recurring tourist movement cascades.

These sequences are then converted into a **directed weighted graph**, where the weights represent the frequency or confidence associated with the observed patterns.

---

## 4. Sequential Centrality Scoring

The mined cascade graph is used to calculate Sequential Centrality for individual zones.

The ranking considers the role of a zone within tourist movement sequences rather than simply counting its visits.

```text
Frequent tourist sequences
            ↓
     Cascade Graph
            ↓
  Sequential Centrality
            ↓
      Zone Ranking
```

The resulting ranking provides candidate zones for further analysis.

---

## 5. Temporal Validation

The project is designed to evaluate predictions using a **time-based split**.

```text
Historical Data
      │
      ▼
Mine Cascades
      │
      ▼
Calculate Sequential Centrality
      │
      ▼
Rank Candidate Zones
      │
      ▼
──────────────────────────
      │
      ▼
Future Data
      │
      ▼
Observe Later Retail Activity
      │
      ▼
Validate Predictions
```

The earlier time period is used to discover patterns and rank zones, while a later period is used to determine whether highly ranked zones correspond to subsequent luxury retail growth or store openings.

---

# ⚖️ Baseline Comparison

TourCascade can be evaluated against simpler approaches.

### 1. Raw Footfall

Ranks zones according to the number of visitors.

```text
Zone Importance = Visitor Count
```

### 2. Static Co-location

Looks at spatial/category associations without explicitly modelling the order in which tourists visit locations.

### 3. TourCascade

Considers:

```text
Spatial relationships
        +
Temporal ordering
        +
Tourist movement sequences
        +
Sequence frequency / confidence
        +
Downstream destination importance
```

This comparison helps investigate whether **sequential movement information** provides additional insight beyond static spatial or footfall-based analysis.

---

# 🧠 Explainable Recommendations

A major objective of TourCascade is **interpretability**.

Instead of producing only:

```text
Zone X → Score: 0.82
```

the system aims to show the mobility patterns behind the recommendation.

For example:

```text
Recommended Zone: Zone X

Supporting Cascades:

Hotel District A
       ↓
Landmark B
       ↓
Zone X

Hotel District C
       ↓
Restaurant D
       ↓
Zone X

Landmark B
       ↓
Shopping Area E
       ↓
Zone X
```

This allows a recommendation to be traced back to the **actual tourist sequences** that contributed to the zone's sequential importance.

---

# 🗺️ Visualization

TourCascade is designed to provide spatial and analytical visualizations of the discovered patterns.

The visualization layer can include:

* Tourist mobility zones
* Sequential movement patterns
* Ranked candidate zones
* Cascade paths
* Supporting sequences
* Spatial distribution of recommendations

An interactive map can be used to explore the relationship between tourist movement and candidate flagship locations.

---

# 📊 Evaluation

The project evaluates whether zones identified from historical tourist movement patterns correspond to relevant activity in a later time period.

### Precision@K

Measures how many of the top-K recommended zones correspond to relevant future zones.

### Recall@K

Measures how many relevant future zones are captured among the top-K recommendations.

### Rank Correlation

Measures the relationship between the historical sequential ranking and later observed activity.

The proposed methodology also supports statistical comparison against simpler baseline approaches.

> **Final numerical results will be reported here once the experimental evaluation is finalized.**

---

# 🏗️ System Pipeline

```text
┌─────────────────────────────┐
│   Tourist Mobility Data     │
│   + POI / Retail Data       │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│     Data Preprocessing      │
│   Cleaning + Temporal Sort  │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│    H3 Spatial Mapping       │
│     City → Spatial Zones    │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   Sequential Pattern Mining │
│ PrefixSpan + Spatial Rules  │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│     Cascade Graph           │
│   Directed + Weighted       │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   Sequential Centrality     │
│       Zone Ranking           │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│     Temporal Validation     │
│       + Baselines           │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Explainable Recommendations │
│       + Visualization       │
└─────────────────────────────┘
```

---

# 🛠️ Technology Stack

| Category              | Technologies                  |
| --------------------- | ----------------------------- |
| Programming           | Python 3.x                    |
| Querying              | SQL                           |
| Data Processing       | Pandas, NumPy                 |
| Geospatial Processing | GeoPandas, Shapely            |
| Spatial Indexing      | H3                            |
| Sequential Mining     | PrefixSpan                    |
| Graph Analysis        | NetworkX                      |
| Evaluation            | Scikit-learn                  |
| Statistical Analysis  | SciPy, Statsmodels            |
| Visualization         | Matplotlib, Seaborn, Plotly   |
| Interactive Maps      | Folium / Kepler.gl            |
| Interactive Demo      | Streamlit / Gradio            |
| Experiment Tracking   | Weights & Biases *(optional)* |

These technologies follow the proposed project architecture documented in the original SSDM assignment.

---

# 📁 Repository Structure

```text
TourCascade_SSDM-Project/
│
├── data/
│   └── raw/
│       └── Raw mobility / POI data
│
├── src/
│   └── Project source code
│
├── figures/
│   └── Generated visualizations
│
├── results/
│   └── Generated analysis results
│
├── main.py
├── output.py
├── generate_deck.py
├── TourCascade_Review2_Submission.pptx
└── README.md
```

---

# 🚀 Installation & Usage

## Clone the repository

```bash
git clone https://github.com/TannyaP/TourCascade_SSDM-Project.git
cd TourCascade_SSDM-Project
```

## Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install dependencies

If the repository contains a `requirements.txt`:

```bash
pip install -r requirements.txt
```

Otherwise, install the required packages:

```bash
pip install pandas numpy geopandas shapely h3 prefixspan networkx scikit-learn scipy statsmodels matplotlib seaborn plotly folium
```

## Run the project

```bash
python main.py
```

## Generate outputs

```bash
python output.py
```

---

# 🔬 Research Questions

TourCascade is built around four primary research questions:

### RQ1

Can tourist mobility sequences reveal spatial opportunities that are not captured by raw footfall?

### RQ2

Can Sequential Centrality identify zones that subsequently become relevant luxury retail locations?

### RQ3

Does incorporating the **order and temporal nature of tourist movement** improve hotspot discovery compared with static spatial analysis?

### RQ4

Can luxury flagship placement recommendations be explained using the actual tourist mobility cascades that generated them?

---

# 💎 Application: Luxury Flagship Placement

The primary application of TourCascade is **luxury retail location intelligence**.

Potential applications include supporting analysis for:

* Luxury fashion brands
* Luxury retail expansion
* Retail real-estate analysis
* Tourism-oriented retail planning
* Urban retail analytics

The system is intended as a **decision-support and analytical framework**, rather than a replacement for human location strategy.

---

# 🌍 Why Tourist Mobility?

Luxury retail demand in major tourist destinations is influenced not only by where tourists are located, but also by **how they move between destinations**.

Consider:

```text
Hotel District
      ↓
Historic Landmark
      ↓
Luxury Retail Area
      ↓
Restaurant
      ↓
Neighbouring Shopping Zone
```

If the same movement structure occurs repeatedly across many tourists, the sequence itself contains information about how tourism demand flows through the city.

TourCascade attempts to capture this information computationally.

---

# 🔮 Future Scope

Future extensions can include:

* Larger multi-city mobility datasets
* Additional luxury retail datasets
* Actual store-opening and store-growth validation
* Tourist spending or transaction-value signals
* Dynamic time-window optimization
* Advanced sequential-centrality formulations
* Additional graph-based ranking techniques
* Real-time mobility streams
* Interactive Streamlit/Gradio deployment
* Automated experiment tracking
* More extensive statistical baseline comparison

---

## ⭐ Project Summary

> **TourCascade explores whether the way tourists move through a city can reveal where luxury retail opportunities may emerge next.**

By combining **spatial representation, sequential pattern mining, tourist mobility cascades, Sequential Centrality, temporal validation and explainable recommendations**, the project aims to move from static **“where are tourists?”** analysis toward dynamic **“where is tourist demand flowing?”** analysis.

---
