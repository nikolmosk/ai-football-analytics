"""Market-pricing helpers for decimal odds.

These are arithmetic primitives, not a claim that model probabilities are
accurate. Settlement-aware markets with pushes/half outcomes need richer logic.
"""
from __future__ import annotations

import math
from collections.abc import Sequence


def implied_probability(decimal_odds: float) -> float:
    _validate_odds(decimal_odds)
    return 1.0 / decimal_odds


def fair_decimal_odds(model_probability: float) -> float:
    _validate_probability(model_probability)
    if model_probability == 0:
        return math.inf
    return 1.0 / model_probability


def devig_proportional(decimal_odds: Sequence[float]) -> list[float]:
    if len(decimal_odds) < 2:
        raise ValueError("at least two mutually exclusive outcomes are required")
    raw = [implied_probability(o) for o in decimal_odds]
    total = sum(raw)
    if not math.isfinite(total) or total <= 0:
        raise ValueError("invalid implied probability sum")
    return [p / total for p in raw]


def expected_value_per_unit(model_probability: float, decimal_odds: float) -> float:
    """Expected net return per 1-unit stake for a binary, no-push market."""
    _validate_probability(model_probability)
    _validate_odds(decimal_odds)
    return model_probability * decimal_odds - 1.0


def edge_percentage_points(model_probability: float, market_probability: float) -> float:
    _validate_probability(model_probability)
    _validate_probability(market_probability)
    return 100.0 * (model_probability - market_probability)


def _validate_probability(value: float) -> None:
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError("probability must be finite and between 0 and 1")


def _validate_odds(value: float) -> None:
    if not math.isfinite(value) or value <= 1.0:
        raise ValueError("decimal odds must be finite and greater than 1.0")
