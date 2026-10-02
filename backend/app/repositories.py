from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Competition, Match, OddsSnapshot, Season, Team
from app.providers.base import EventSnapshot


def _parse_time(value) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


async def _team(session: AsyncSession, key: str, name: str) -> Team:
    obj = (await session.execute(select(Team).where(Team.provider_key == key))).scalar_one_or_none()
    if obj is None:
        obj = Team(provider_key=key, name=name)
        session.add(obj)
        await session.flush()
    elif obj.name != name:
        obj.name = name
    return obj


async def _competition(session: AsyncSession, key: str, name: str) -> Competition:
    obj = (await session.execute(select(Competition).where(Competition.provider_key == key))).scalar_one_or_none()
    if obj is None:
        obj = Competition(provider_key=key, name=name, sport="football")
        session.add(obj)
        await session.flush()
    elif obj.name != name:
        obj.name = name
    return obj


async def _season(session: AsyncSession, competition_id: int, provider_key: str) -> Season:
    obj = (await session.execute(select(Season).where(
        Season.competition_id == competition_id, Season.provider_key == provider_key
    ))).scalar_one_or_none()
    if obj is None:
        obj = Season(
            competition_id=competition_id,
            provider_key=provider_key,
            name="Current provider feed",
        )
        session.add(obj)
        await session.flush()
    return obj


def _point_key(point) -> str:
    if point is None:
        return "NULL"
    return f"{float(point):.6f}"


async def persist_event(
    session: AsyncSession,
    event: EventSnapshot,
    *,
    provider: str = "the-odds-api",
) -> Match:
    participants = event.participants.value
    sport_key = str(event.payload.get("sport_key") or event.competition.value)
    competition_name = str(event.payload.get("sport_title") or sport_key)
    competition = await _competition(session, f"{event.sport}:{sport_key}", competition_name)
    season = await _season(session, competition.id, "current")
    home = await _team(session, f"{event.sport}:{participants['home']}", str(participants["home"]))
    away = await _team(session, f"{event.sport}:{participants['away']}", str(participants["away"]))

    match = (await session.execute(select(Match).where(
        Match.provider == provider, Match.provider_event_id == event.event_id
    ))).scalar_one_or_none()
    if match is None:
        match = Match(
            provider=provider,
            provider_event_id=event.event_id,
            competition_id=competition.id,
            season_id=season.id,
            home_team_id=home.id,
            away_team_id=away.id,
            start_time_utc=_parse_time(event.start_time_utc.value),
            status=str(event.status.value),
            retrieved_at=event.retrieved_at,
        )
        session.add(match)
        await session.flush()
    else:
        match.competition_id = competition.id
        match.season_id = season.id
        match.home_team_id = home.id
        match.away_team_id = away.id
        match.start_time_utc = _parse_time(event.start_time_utc.value)
        match.status = str(event.status.value)
        match.retrieved_at = event.retrieved_at

    for market in event.markets:
        observed = _parse_time(market["last_update"]) if market.get("last_update") else event.retrieved_at
        for outcome in market.get("outcomes", []):
            price = outcome.get("price")
            if not isinstance(price, (int, float)) or price <= 1:
                continue
            point = outcome.get("point")
            session.add(OddsSnapshot(
                match_id=match.id,
                bookmaker_key=str(market.get("bookmaker_key") or market.get("bookmaker") or "unknown"),
                bookmaker_name=str(market.get("bookmaker") or "unknown"),
                market_key=str(market.get("market") or "unknown"),
                selection=str(outcome.get("name") or ""),
                point=point,
                point_key=_point_key(point),
                decimal_odds=float(price),
                observed_at=observed,
                retrieved_at=event.retrieved_at,
                source_url=event.markets[0].get("source_url") if event.markets else None,
                raw={"outcome": outcome, "market": market},
            ))
    return match


async def persist_events(session: AsyncSession, events: list[EventSnapshot], *, provider: str = "the-odds-api") -> int:
    count = 0
    for event in events:
        await persist_event(session, event, provider=provider)
        count += 1
    await session.commit()
    return count
