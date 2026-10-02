"""Transparent independent-Poisson football score model.

This module calculates probabilities from caller-supplied expected goals. It does
not estimate expected goals, fetch current data, or claim calibration.
"""
from __future__ import annotations

import math
from typing import Any


def _poisson_pmf(lam: float, k: int) -> float:
    if lam < 0 or not math.isfinite(lam):
        raise ValueError("lambda must be finite and non-negative")
    if k < 0:
        return 0.0
    if lam == 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lam + k * math.log(lam) - math.lgamma(k + 1))


def score_matrix(home_xg: float, away_xg: float, max_goals: int = 10) -> list[list[float]]:
    """Return joint score probabilities truncated at max_goals per team."""
    if not math.isfinite(home_xg) or not math.isfinite(away_xg):
        raise ValueError("expected goals must be finite")
    if home_xg < 0 or away_xg < 0:
        raise ValueError("expected goals must be non-negative")
    if not isinstance(max_goals, int) or max_goals < 1 or max_goals > 30:
        raise ValueError("max_goals must be an integer from 1 to 30")
    home = [_poisson_pmf(home_xg, i) for i in range(max_goals + 1)]
    away = [_poisson_pmf(away_xg, i) for i in range(max_goals + 1)]
    return [[h * a for a in away] for h in home]


def outcome_probabilities(home_xg: float, away_xg: float, max_goals: int = 10) -> dict[str, Any]:
    """Derive regulation 1X2 and total-goal probabilities from scoreline matrix.

    The omitted tail above max_goals is reported; values are not silently
    renormalized, so callers can judge truncation adequacy.
    """
    matrix = score_matrix(home_xg, away_xg, max_goals)
    home_win = draw = away_win = over_25 = btts = 0.0
    for h, row in enumerate(matrix):
        for a, p in enumerate(row):
            if h > a:
                home_win += p
            elif h == a:
                draw += p
            else:
                away_win += p
            if h + a >= 3:
                over_25 += p
            if h >= 1 and a >= 1:
                btts += p
    captured_mass = sum(sum(row) for row in matrix)
    return {
        "home_win": home_win,
        "draw": draw,
        "away_win": away_win,
        "over_2_5": over_25,
        "under_2_5": max(0.0, captured_mass - over_25),
        "btts_yes": btts,
        "btts_no": max(0.0, captured_mass - btts),
        "captured_probability_mass": captured_mass,
        "truncated_tail_probability": max(0.0, 1.0 - captured_mass),
        "model": "independent_poisson",
        "scope": "regulation_time",
        "calibration_status": "UNVERIFIED",
    }
