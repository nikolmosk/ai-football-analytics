"""FastAPI application for AI Football Analytics."""
from contextlib import asynccontextmanager\nfrom datetime import datetime, timezone
from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.football_poisson import outcome_probabilities
from app.analytics.markets import devig_proportional, edge_percentage_points, expected_value_per_unit, fair_decimal_odds
from app.config import get_odds_api_base_url, get_odds_api_key, get_odds_api_markets, get_odds_api_regions, get_odds_api_sport, get_redis_url
from app.db import SessionLocal
from app.models import Match, OddsSnapshot, Team, TeamMatchStats
from app.providers.base import ProviderError
from app.providers.registry import ProviderRegistry
from app.providers.the_odds_api import TheOddsAPIProvider
from app.repositories import persist_events\nfrom app.ingestion import safe_sync_odds\nfrom app.scheduler import configure_scheduler, scheduler\nfrom redis.asyncio import Redis
from app.form import FormRecord, build_form, cutoff_for_match

provider_registry = ProviderRegistry()
odds_provider = TheOddsAPIProvider(
    api_key=get_odds_api_key(), base_url=get_odds_api_base_url(),
    sport=get_odds_api_sport(), regions=get_odds_api_regions(), markets=get_odds_api_markets(),
)
provider_registry.register("football", odds_provider)

app = FastAPI(title="AI Football Analytics API", version="0.6.0",
              description="Football analytics backend with normalized match and odds ingestion.")


async def db_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


class ProbabilityRequest(BaseModel):
    home: float = Field(ge=0, le=1)
    draw: float = Field(ge=0, le=1)
    away: float = Field(ge=0, le=1)


class FootballPoissonRequest(BaseModel):
    home_xg: float = Field(ge=0, le=10)
    away_xg: float = Field(ge=0, le=10)
    max_goals: int = Field(default=12, ge=1, le=30)


class BinaryMarketRequest(BaseModel):
    model_probability: float = Field(ge=0, le=1)
    decimal_odds: float = Field(gt=1)
    market_probability_devig: float | None = Field(default=None, ge=0, le=1)


class DevigRequest(BaseModel):
    decimal_odds: list[float] = Field(min_length=2)


@app.get("/api/v1/data/providers")
def data_provider_status() -> dict[str, object]:
    return provider_registry.status()


@app.get("/api/v1/data/providers/football/health")
async def football_provider_health() -> dict[str, str]:
    return await odds_provider.healthcheck()


@app.post("/api/v1/data/football/sync")
async def sync_football_events(session: AsyncSession = Depends(db_session)) -> dict[str, object]:
    try:
        events = await odds_provider.get_events()
        count = await persist_events(session, events, provider=odds_provider.provider_name)
    except ProviderError as exc:
        await session.rollback()
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"provider": odds_provider.provider_name, "events_seen": len(events), "events_persisted": count,
            "retrieved_at": datetime.now(timezone.utc).isoformat()}


@app.get("/api/v1/data/football/events/{event_id}")
async def football_event(event_id: str) -> dict[str, object]:
    try:
        snapshot = await odds_provider.get_event(event_id)
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return snapshot.model_dump(mode="json")


@app.get("/api/v1/matches")
async def list_matches(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    status: str | None = None,
    session: AsyncSession = Depends(db_session),
) -> dict[str, object]:
    query = select(Match).order_by(Match.start_time_utc).offset(offset).limit(limit)
    if status:
        query = query.where(Match.status == status)
    matches = (await session.execute(query)).scalars().all()
    return {"items": [_match_dto(m) for m in matches], "limit": limit, "offset": offset, "count": len(matches)}


@app.get("/api/v1/matches/{match_id}")
async def get_match(match_id: int, session: AsyncSession = Depends(db_session)) -> dict[str, object]:
    match = await session.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return _match_dto(match)


@app.get("/api/v1/matches/{match_id}/odds")
async def get_match_odds(
    match_id: int,
    limit: int = Query(default=200, ge=1, le=1000),
    session: AsyncSession = Depends(db_session),
) -> dict[str, object]:
    if await session.get(Match, match_id) is None:
        raise HTTPException(status_code=404, detail="Match not found")
    rows = (await session.execute(
        select(OddsSnapshot).where(OddsSnapshot.match_id == match_id).order_by(OddsSnapshot.observed_at.desc()).limit(limit)
    )).scalars().all()
    return {"items": [_odds_dto(row) for row in rows], "count": len(rows), "limit": limit}


def _match_dto(match: Match) -> dict[str, object]:
    return {
        "id": match.id, "provider": match.provider, "provider_event_id": match.provider_event_id,
        "competition_id": match.competition_id, "season_id": match.season_id,
        "home_team_id": match.home_team_id, "away_team_id": match.away_team_id,
        "start_time_utc": match.start_time_utc.isoformat(), "status": match.status,
        "retrieved_at": match.retrieved_at.isoformat(),
    }


def _odds_dto(row: OddsSnapshot) -> dict[str, object]:
    return {
        "id": row.id, "bookmaker_key": row.bookmaker_key, "bookmaker_name": row.bookmaker_name,
        "market_key": row.market_key, "selection": row.selection, "point": row.point,
        "decimal_odds": row.decimal_odds, "observed_at": row.observed_at.isoformat(),
        "retrieved_at": row.retrieved_at.isoformat(), "source_url": row.source_url,
    }




@app.get("/api/v1/matches/{match_id}/stats")
async def get_match_stats(match_id: int, session: AsyncSession = Depends(db_session)) -> dict[str, object]:
    if await session.get(Match, match_id) is None:
        raise HTTPException(status_code=404, detail="Match not found")
    rows = (await session.execute(
        select(TeamMatchStats).where(TeamMatchStats.match_id == match_id).order_by(TeamMatchStats.team_id)
    )).scalars().all()
    return {"items": [_stats_dto(row) for row in rows], "count": len(rows), "data_status": "VERIFIED" if rows else "DATA_INSUFFICIENT"}


@app.get("/api/v1/teams/{team_id}/form")
async def get_team_form(
    team_id: int,
    limit: int = Query(default=5, ge=1, le=20),
    venue: str = Query(default="all", pattern="^(all|home|away)$"),
    before_match_id: int | None = Query(default=None, ge=1),
    session: AsyncSession = Depends(db_session),
) -> dict[str, object]:
    team = await session.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")

    cutoff = datetime.now(timezone.utc)
    if before_match_id is not None:
        target = await session.get(Match, before_match_id)
        if target is None:
            raise HTTPException(status_code=404, detail="Target match not found")
        cutoff = cutoff_for_match(target.start_time_utc)

    rows = (await session.execute(
        select(TeamMatchStats, Match)
        .join(Match, TeamMatchStats.match_id == Match.id)
        .where(
            TeamMatchStats.team_id == team_id,
            Match.start_time_utc < cutoff,
            Match.status.in_(["completed", "complete", "finished", "ft"]),
        )
        .order_by(Match.start_time_utc.desc())
    )).all()

    records: list[FormRecord] = []
    for stats, match in rows:
        is_home = match.home_team_id == team_id
        if venue != "all" and ((venue == "home") != is_home):
            continue
        opponent_id = match.away_team_id if is_home else match.home_team_id
        opponent = await session.get(Team, opponent_id)
        records.append(FormRecord(
            match_id=match.id, team_id=team_id, opponent_team_id=opponent_id,
            opponent_name=opponent.name if opponent else str(opponent_id),
            venue="home" if is_home else "away", start_time_utc=match.start_time_utc,
            goals_for=stats.goals_for, goals_against=stats.goals_against,
            shots=stats.shots, shots_on_target=stats.shots_on_target,
            possession_pct=stats.possession_pct, corners=stats.corners,
            fouls=stats.fouls, yellow_cards=stats.yellow_cards,
            red_cards=stats.red_cards, xg=stats.xg,
            source=stats.source, status=stats.status,
        ))

    form = build_form(records, limit=limit)
    form.update({
        "team_id": team_id,
        "venue": venue,
        "before_match_id": before_match_id,
        "cutoff_utc": cutoff.isoformat(),
        "data_note": "Only stored provider observations are included; missing metrics are not inferred.",
    })
    return form


def _stats_dto(row: TeamMatchStats) -> dict[str, object]:
    return {
        "id": row.id, "match_id": row.match_id, "team_id": row.team_id,
        "source": row.source, "status": row.status,
        "observed_at": row.observed_at.isoformat(), "retrieved_at": row.retrieved_at.isoformat(),
        "goals_for": row.goals_for, "goals_against": row.goals_against,
        "shots": row.shots, "shots_on_target": row.shots_on_target,
        "possession_pct": row.possession_pct, "corners": row.corners,
        "fouls": row.fouls, "yellow_cards": row.yellow_cards, "red_cards": row.red_cards,
        "xg": row.xg, "source_url": row.source_url,
    }

@app.get("/health")
async def health() -> dict[str, str]:
    provider = await odds_provider.healthcheck()
    return {"status": "ok", "data_mode": "live_provider_configured", "odds_provider": provider["status"]}


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "AI Football Analytics API", "version": "0.6.0", "status": "development", "data_status": "SOURCE_GATED"}


@app.post("/api/v1/analytics/probabilities/validate")
def validate_probabilities(payload: ProbabilityRequest) -> dict[str, object]:
    total = payload.home + payload.draw + payload.away
    valid = abs(total - 1.0) <= 0.01
    return {"valid": valid, "sum": round(total, 6), "message": "Probabilities sum to approximately 1." if valid else "DATA INSUFFICIENT: probabilities must sum to approximately 1."}


@app.post("/api/v1/analytics/football/poisson")
def football_poisson(payload: FootballPoissonRequest) -> dict[str, object]:
    result = outcome_probabilities(payload.home_xg, payload.away_xg, payload.max_goals)
    result["input_status"] = "CALLER_SUPPLIED_UNVERIFIED"
    result["warning"] = "Expected-goal inputs were supplied by the caller; no match data was fetched. The model is not calibrated and the score matrix is truncated."
    return result


@app.post("/api/v1/markets/binary")
def binary_market(payload: BinaryMarketRequest) -> dict[str, float | None | str]:
    probability = payload.model_probability
    fair_odds = fair_decimal_odds(probability)
    ev = expected_value_per_unit(probability, payload.decimal_odds)
    edge = edge_percentage_points(probability, payload.market_probability_devig) if payload.market_probability_devig is not None else None
    return {"model_probability": probability, "decimal_odds": payload.decimal_odds, "fair_decimal_odds": fair_odds if fair_odds != float("inf") else None, "expected_value_per_unit": ev, "edge_percentage_points": edge, "status": "UNVERIFIED", "warning": "Arithmetic only; input probability and market equivalence are not verified."}


@app.post("/api/v1/markets/devig")
def devig_market(payload: DevigRequest) -> dict[str, object]:
    probabilities = devig_proportional(payload.decimal_odds)
    return {"method": "proportional", "decimal_odds": payload.decimal_odds, "market_probabilities": probabilities, "sum": sum(probabilities), "status": "UNVERIFIED", "warning": "Inputs must be mutually exclusive outcomes from the same market snapshot."}
