from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from statistics import mean
from typing import Literal

Venue = Literal["all", "home", "away"]


@dataclass(frozen=True)
class FormRecord:
    match_id: int
    team_id: int
    opponent_team_id: int
    opponent_name: str
    venue: Literal["home", "away"]
    start_time_utc: datetime
    goals_for: int | None
    goals_against: int | None
    shots: int | None
    shots_on_target: int | None
    possession_pct: float | None
    corners: int | None
    fouls: int | None
    yellow_cards: int | None
    red_cards: int | None
    xg: float | None
    source: str
    status: str


def _avg(values: list[float | int | None]) -> float | None:
    clean = [float(v) for v in values if v is not None]
    return round(mean(clean), 4) if clean else None


def _result(goals_for: int | None, goals_against: int | None) -> str:
    if goals_for is None or goals_against is None:
        return "UNKNOWN"
    if goals_for > goals_against:
        return "W"
    if goals_for < goals_against:
        return "L"
    return "D"


def build_form(records: list[FormRecord], limit: int = 5) -> dict[str, object]:
    selected = sorted(records, key=lambda r: r.start_time_utc, reverse=True)[:limit]
    known_results = [_result(r.goals_for, r.goals_against) for r in selected]
    known = [r for r in selected if r.goals_for is not None and r.goals_against is not None]
    wins = sum(_result(r.goals_for, r.goals_against) == "W" for r in known)
    draws = sum(_result(r.goals_for, r.goals_against) == "D" for r in known)
    losses = sum(_result(r.goals_for, r.goals_against) == "L" for r in known)
    return {
        "matches_requested": limit,
        "matches_returned": len(selected),
        "matches_with_score": len(known),
        "results": known_results,
        "record": {"wins": wins, "draws": draws, "losses": losses},
        "points": wins * 3 + draws,
        "goals_for_avg": _avg([r.goals_for for r in known]),
        "goals_against_avg": _avg([r.goals_against for r in known]),
        "xg_avg": _avg([r.xg for r in selected]),
        "shots_avg": _avg([r.shots for r in selected]),
        "shots_on_target_avg": _avg([r.shots_on_target for r in selected]),
        "possession_avg": _avg([r.possession_pct for r in selected]),
        "corners_avg": _avg([r.corners for r in selected]),
        "data_status": "VERIFIED" if known and all(r.status == "VERIFIED" for r in selected) else (
            "PARTIAL" if selected else "DATA_INSUFFICIENT"
        ),
    }


def cutoff_for_match(start_time: datetime) -> datetime:
    return start_time if start_time.tzinfo else start_time.replace(tzinfo=timezone.utc)
