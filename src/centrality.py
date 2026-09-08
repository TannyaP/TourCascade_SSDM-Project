import networkx as nx
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def build_cascade_graph(patterns: pd.DataFrame) -> nx.DiGraph:
    """Transforms mined patterns into a directed, weighted cascade graph."""
    G = nx.DiGraph()
    for _, row in patterns.iterrows():
        source = row["from_zone"]
        target = row["to_zone"]
        weight = row["support"] * row["confidence"]

        G.add_edge(
            source,
            target,
            weight=weight,
            confidence=row["confidence"],
            support=row["support"]
        )
    return G

def calculate_sequential_centrality(G: nx.DiGraph) -> pd.DataFrame:
    """Computes the Sequential Centrality metric via downstream inflow and PageRank."""
    cols = ["zone_id", "weighted_inflow", "downstream_count", "pagerank", "sequential_centrality"]
    if len(G.nodes) == 0:
        return pd.DataFrame(columns=cols)

    pagerank = nx.pagerank(G, weight="weight")
    records = []

    for node in G.nodes:
        incoming = list(G.in_edges(node, data=True))
        weighted_inflow = sum(data.get("weight", 0.0) for _, _, data in incoming)
        downstream_count = len(incoming)

        records.append({
            "zone_id": node,
            "weighted_inflow": weighted_inflow,
            "downstream_count": downstream_count,
            "pagerank": pagerank.get(node, 0.0)
        })

    scores = pd.DataFrame(records)
    scaler = MinMaxScaler()

    scores["weighted_inflow_norm"] = scaler.fit_transform(scores[["weighted_inflow"]])
    scores["pagerank_norm"] = scaler.fit_transform(scores[["pagerank"]])

    # Weighted downstream convergence scoring formula
    scores["sequential_centrality"] = (
        0.7 * scores["weighted_inflow_norm"] +
        0.3 * scores["pagerank_norm"]
    )

    return scores.sort_values(
        by="sequential_centrality",
        ascending=False
    ).reset_index(drop=True)