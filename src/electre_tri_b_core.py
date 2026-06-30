"""Transparent ELECTRE TRI-B implementation used by the study."""
from __future__ import annotations

import numpy as np


def partial_concordance(a: float, b: float, q: float, p: float) -> float:
    difference = b - a
    if difference <= q:
        return 1.0
    if difference >= p:
        return 0.0
    return (p - difference) / (p - q)


def partial_discordance(a: float, b: float, p: float, v: float) -> float:
    difference = b - a
    if difference <= p:
        return 0.0
    if difference >= v:
        return 1.0
    return (difference - p) / (v - p)


def credibility(a, b, weights, q, p, v) -> float:
    """Return the credibility of the outranking relation a S b.

    All criteria are assumed to be oriented so that larger values indicate
    greater investigation priority.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    weights = np.asarray(weights, dtype=float)

    concordances = np.array(
        [partial_concordance(ai, bi, qi, pi) for ai, bi, qi, pi in zip(a, b, q, p)],
        dtype=float,
    )
    global_concordance = float(np.dot(weights, concordances) / weights.sum())

    discordances = np.array(
        [partial_discordance(ai, bi, pi, vi) for ai, bi, pi, vi in zip(a, b, p, v)],
        dtype=float,
    )

    sigma = global_concordance
    for discordance in discordances:
        if discordance > global_concordance:
            sigma *= (1.0 - discordance) / (1.0 - global_concordance)
    return float(sigma)


def pessimistic_assignment(data, profiles, weights, q, p, v, cut_level=0.60):
    """Assign alternatives to ordered classes using the pessimistic rule.

    Classes are returned as integers from 0 to len(profiles), where 0 is the
    lowest class. Profiles must be ordered from the lowest to the highest
    boundary.
    """
    data = np.asarray(data, dtype=float)
    profiles = np.asarray(profiles, dtype=float)
    assignments = []

    for alternative in data:
        assigned_class = 0
        for profile_index in range(len(profiles) - 1, -1, -1):
            if credibility(
                alternative, profiles[profile_index], weights, q, p, v
            ) >= cut_level:
                assigned_class = profile_index + 1
                break
        assignments.append(assigned_class)

    return np.asarray(assignments, dtype=int)
