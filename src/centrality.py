"""
TourCascade - Sequential Centrality

Builds a directed cascade graph from mined sequential patterns.

Sequential Centrality combines:

1. confidence-weighted downstream influence
2. PageRank over the sequential graph
3. upstream diversity

The final score is normalized to [0, 1].
"""

import networkx as nx
import numpy as np
import pandas as pd


def build_cascade_graph(patterns):
    """
    Build directed weighted graph.

    For every sequential pattern:

        A -> B -> C

    edges are created:

        A -> B
        B -> C

    Edge weights combine support and confidence.
    """

    G = nx.DiGraph()

    if patterns is None or len(patterns) == 0:
        return G

    for _, row in patterns.iterrows():

        pattern = row.get("pattern_tuple")

        if pattern is None:
            pattern_string = row.get("pattern", "")
            pattern = tuple(
                x.strip()
                for x in str(pattern_string).split("->")
            )

        pattern = list(pattern)

        if len(pattern) < 2:
            continue

        support = float(row.get("support", 0))
        confidence = float(row.get("confidence", 0))

        # Combined edge weight
        weight = support * confidence

        for i in range(len(pattern) - 1):

            source = str(pattern[i])
            target = str(pattern[i + 1])

            if source == target:
                continue

            if G.has_edge(source, target):
                G[source][target]["weight"] += weight
            else:
                G.add_edge(
                    source,
                    target,
                    weight=weight,
                )

    return G


def _normalize_series(series):
    """
    Min-max normalization.
    """

    series = pd.Series(series, dtype=float)

    if len(series) == 0:
        return series

    min_value = series.min()
    max_value = series.max()

    if max_value == min_value:
        return pd.Series(
            np.ones(len(series)),
            index=series.index,
        )

    return (
        (series - min_value)
        / (max_value - min_value)
    )


def calculate_sequential_centrality(
    G,
    alpha=0.50,
    beta=0.30,
    gamma=0.20,
):
    """
    Calculate Sequential Centrality.

    SC(z) =
        alpha * downstream influence
        + beta * PageRank
        + gamma * upstream diversity

    Downstream influence is based on weighted incoming
    sequential transitions.

    Upstream diversity rewards zones reached from
    different predecessor zones.
    """

    if G is None or G.number_of_nodes() == 0:
        return pd.DataFrame(
            columns=[
                "zone_id",
                "sequential_centrality",
                "downstream_count",
                "weighted_inflow",
                "pagerank",
                "upstream_diversity",
            ]
        )

    nodes = list(G.nodes())

    # Weighted PageRank
    try:
        pagerank = nx.pagerank(
            G,
            weight="weight",
        )
    except Exception:
        pagerank = {
            node: 0.0
            for node in nodes
        }

    rows = []

    for zone in nodes:

        predecessors = list(
            G.predecessors(zone)
        )

        weighted_inflow = sum(
            G[p][zone].get("weight", 0.0)
            for p in predecessors
        )

        downstream_count = len(predecessors)

        # Diversity is number of unique upstream nodes
        upstream_diversity = len(
            set(predecessors)
        )

        rows.append(
            {
                "zone_id": str(zone),
                "weighted_inflow": weighted_inflow,
                "downstream_count": downstream_count,
                "pagerank": pagerank.get(zone, 0.0),
                "upstream_diversity": upstream_diversity,
            }
        )

    result = pd.DataFrame(rows)

    result["inflow_norm"] = _normalize_series(
        result["weighted_inflow"]
    )

    result["pagerank_norm"] = _normalize_series(
        result["pagerank"]
    )

    result["diversity_norm"] = _normalize_series(
        result["upstream_diversity"]
    )

    result["sequential_centrality"] = (
        alpha * result["inflow_norm"]
        + beta * result["pagerank_norm"]
        + gamma * result["diversity_norm"]
    )

    result = result.sort_values(
        "sequential_centrality",
        ascending=False,
    ).reset_index(drop=True)

    return result[
        [
            "zone_id",
            "sequential_centrality",
            "downstream_count",
            "weighted_inflow",
            "pagerank",
            "upstream_diversity",
        ]
    ]