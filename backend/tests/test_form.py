from datetime import datetime, timezone, timedelta

from app.form import FormRecord, build_form


def record(match_id: int, days_ago: int, goals_for: int | None, goals_against: int | None, venue: str = "home"):
    return FormRecord(
        match_id=match_id, team_id=1, opponent_team_id=match_id + 100,
        opponent_name=f"Opponent {match_id}", venue=venue,
        start_time_utc=datetime.now(timezone.utc) - timedelta(days=days_ago),
        goals_for=goals_for, goals_against=goals_against,
        shots=10, shots_on_target=4, possession_pct=55.0,
        corners=5, fouls=9, yellow_cards=1, red_cards=0,
        xg=None, source="fixture-test", status="VERIFIED",
    )


def test_build_form_uses_latest_n_matches():
    result = build_form([
        record(1, 10, 2, 0),
        record(2, 5, 1, 1),
        record(3, 2, 0, 1),
        record(4, 1, 3, 0),
    ], limit=3)
    assert result["matches_returned"] == 3
    assert result["record"] == {"wins": 2, "draws": 1, "losses": 0}
    assert result["points"] == 7
    assert result["goals_for_avg"] == 1.3333


def test_build_form_does_not_turn_missing_scores_into_results():
    result = build_form([record(1, 1, None, None)], limit=5)
    assert result["matches_returned"] == 1
    assert result["matches_with_score"] == 0
    assert result["results"] == ["UNKNOWN"]
    assert result["record"] == {"wins": 0, "draws": 0, "losses": 0}
    assert result["data_status"] == "PARTIAL"
