import math

import pytest

from backend.app.analytics.football_poisson import outcome_probabilities, score_matrix
from backend.app.analytics.markets import (
    devig_proportional,
    edge_percentage_points,
    expected_value_per_unit,
    fair_decimal_odds,
    implied_probability,
)


def test_market_math():
    assert implied_probability(2.0) == pytest.approx(0.5)
    assert fair_decimal_odds(0.25) == pytest.approx(4.0)
    assert expected_value_per_unit(0.5, 2.2) == pytest.approx(0.1)
    assert edge_percentage_points(0.55, 0.5) == pytest.approx(5.0)


def test_devig_sums_to_one():
    probs = devig_proportional([2.0, 3.5, 4.0])
    assert sum(probs) == pytest.approx(1.0)
    assert all(0 < p < 1 for p in probs)


def test_reject_invalid_odds_and_probability():
    with pytest.raises(ValueError):
        implied_probability(1.0)
    with pytest.raises(ValueError):
        fair_decimal_odds(1.1)
    with pytest.raises(ValueError):
        expected_value_per_unit(0.5, math.inf)


def test_poisson_outcomes_have_reasonable_probability_mass():
    result = outcome_probabilities(1.4, 1.0, max_goals=12)
    assert result["home_win"] > result["away_win"]
    assert result["captured_probability_mass"] > 0.999
    assert result["truncated_tail_probability"] < 0.001
    assert result["calibration_status"] == "UNVERIFIED"


def test_zero_expected_goals():
    matrix = score_matrix(0.0, 0.0, max_goals=3)
    assert matrix[0][0] == pytest.approx(1.0)
    assert sum(sum(row) for row in matrix) == pytest.approx(1.0)
