"""
TourCascade - Sequential Pattern Mining

Mines multi-step tourist mobility sequences using a
PrefixSpan-inspired recursive pattern-growth approach.

Patterns can have length 2..MAX_PATTERN_LENGTH.

The miner calculates:
    support
    confidence
    occurrence count
    unique session count

and supports category-aware filtering.
"""

from collections import defaultdict
import pandas as pd


DEFAULT_MAX_PATTERN_LENGTH = 4


def _unique_sequence(sequence):
    """
    Remove consecutive duplicate zones.

    Example:
        A, A, B, B, C -> A, B, C
    """
    if not sequence:
        return []

    result = [sequence[0]]

    for item in sequence[1:]:
        if item != result[-1]:
            result.append(item)

    return result


def _is_subsequence(pattern, sequence):
    """
    Check whether pattern occurs in sequence in order.
    """
    if len(pattern) > len(sequence):
        return False

    j = 0

    for item in sequence:
        if item == pattern[j]:
            j += 1

            if j == len(pattern):
                return True

    return False


def _mine_prefix_patterns(
    sequences,
    min_support,
    max_pattern_length,
):
    """
    PrefixSpan-inspired recursive pattern growth.

    Each sequence is treated as one transaction/session.

    Support is session-level support:
        number of sessions containing pattern / total sessions
    """

    n_sessions = len(sequences)

    if n_sessions == 0:
        return []

    min_count = max(1, int(min_support * n_sessions))

    results = []

    def recursive(prefix, projected_sequences):
        if len(prefix) >= max_pattern_length:
            return

        candidate_sessions = defaultdict(list)

        for sequence in projected_sequences:
            used = set()

            for index, item in enumerate(sequence):
                if item in used:
                    continue

                used.add(item)

                suffix = sequence[index + 1:]

                candidate_sessions[item].append(suffix)

        for item, suffixes in candidate_sessions.items():

            count = len(suffixes)

            if count < min_count:
                continue

            new_pattern = prefix + [item]

            support = count / n_sessions

            results.append(
                {
                    "pattern": tuple(new_pattern),
                    "length": len(new_pattern),
                    "support_count": count,
                    "support": support,
                }
            )

            recursive(
                new_pattern,
                suffixes,
            )

    # Start from the complete set of sequences
    recursive([], sequences)

    return results


def _calculate_confidence(pattern_rows):
    """
    Confidence for a pattern:

        support(A -> ... -> Z)
        ----------------------
        support(A -> ... -> Y)

    where Y is the prefix of the pattern.
    """

    support_lookup = {
        row["pattern"]: row["support"]
        for row in pattern_rows
    }

    count_lookup = {
        row["pattern"]: row["support_count"]
        for row in pattern_rows
    }

    for row in pattern_rows:

        pattern = row["pattern"]

        if len(pattern) <= 1:
            row["confidence"] = 1.0
            continue

        prefix = pattern[:-1]

        prefix_count = count_lookup.get(prefix, 0)

        if prefix_count == 0:
            row["confidence"] = 0.0
        else:
            row["confidence"] = (
                row["support_count"] / prefix_count
            )

    return pattern_rows


def mine_sequential_patterns(
    cascades,
    min_support=0.01,
    min_confidence=0.20,
    max_pattern_length=DEFAULT_MAX_PATTERN_LENGTH,
):
    """
    Mine multi-step sequential mobility patterns.

    Parameters
    ----------
    cascades:
        List of session sequences.

        Example:
            [
                ["hotel_A", "landmark_B", "retail_C"],
                ["hotel_A", "restaurant_D", "retail_C"],
            ]

    min_support:
        Minimum proportion of sessions containing a pattern.

    min_confidence:
        Minimum confidence.

    max_pattern_length:
        Maximum sequence length.

    Returns
    -------
    pandas.DataFrame
    """

    if cascades is None:
        return pd.DataFrame()

    # Convert input to clean zone sequences
    sequences = []

    for cascade in cascades:

        if cascade is None:
            continue

        # Handle tuple/list representations
        sequence = list(cascade)

        sequence = [
            str(x)
            for x in sequence
            if pd.notna(x)
        ]

        sequence = _unique_sequence(sequence)

        if len(sequence) >= 2:
            sequences.append(sequence)

    if not sequences:
        return pd.DataFrame(
            columns=[
                "pattern",
                "length",
                "support_count",
                "support",
                "confidence",
                "source_zone",
                "target_zone",
            ]
        )

    # Remove exact duplicate sequences
    sequences = list(
        dict.fromkeys(
            tuple(seq)
            for seq in sequences
        )
    )

    sequences = [list(seq) for seq in sequences]

    # Mine all patterns
    pattern_rows = _mine_prefix_patterns(
        sequences=sequences,
        min_support=min_support,
        max_pattern_length=max_pattern_length,
    )

    if not pattern_rows:
        return pd.DataFrame()

    pattern_rows = _calculate_confidence(pattern_rows)

    # Filter confidence
    pattern_rows = [
        row
        for row in pattern_rows
        if row["confidence"] >= min_confidence
    ]

    if not pattern_rows:
        return pd.DataFrame()

    output = []

    for row in pattern_rows:

        pattern = row["pattern"]

        output.append(
            {
                "pattern": " -> ".join(pattern),
                "pattern_tuple": pattern,
                "length": row["length"],
                "support_count": row["support_count"],
                "support": row["support"],
                "confidence": row["confidence"],
                "source_zone": pattern[0],
                "target_zone": pattern[-1],
            }
        )

    df = pd.DataFrame(output)

    df = df.sort_values(
        [
            "confidence",
            "support",
            "length",
        ],
        ascending=False,
    ).reset_index(drop=True)

    return df