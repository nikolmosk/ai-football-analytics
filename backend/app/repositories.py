from __future__ import annotations
from datetime import datetime,timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Competition,Match,OddsSnapshot,Team
from app.providers.base import EventSnapshot
def _parse_time(value): 
    parsed=datetime.fromisoformat(str(value).replace("Z","+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
async def _team(session,key,name):
    obj=(await session.execute(select(Team).where(Team.provider_key==key))).scalar_one_or_none()
    if obj is None: obj=Team(provider_key=key,name=name); session.add(obj); await session.flush()
    return obj
async def _competition(session,key,name):
    obj=(await session.execute(select(Competition).where(Competition.provider_key==key))).scalar_one_or_none()
    if obj is None: obj=Competition(provider_key=key,name=name,sport="football"); session.add(obj); await session.flush()
    return obj
async def persist_event(session:AsyncSession,event:EventSnapshot)->Match:
    p=event.participants.value; comp=await _competition(session,f"{event.sport}:{event.competition.value}",str(event.competition.value))
    home=await _team(session,f"{event.sport}:{p['home']}",str(p["home"])); away=await _team(session,f"{event.sport}:{p['away']}",str(p["away"]))
    match=(await session.execute(select(Match).where(Match.provider=="the-odds-api",Match.provider_event_id==event.event_id))).scalar_one_or_none()
    if match is None:
        match=Match(provider="the-odds-api",provider_event_id=event.event_id,competition_id=comp.id,home_team_id=home.id,away_team_id=away.id,start_time_utc=_parse_time(event.start_time_utc.value),status=str(event.status.value),retrieved_at=event.retrieved_at); session.add(match); await session.flush()
    else:
        match.competition_id=comp.id; match.home_team_id=home.id; match.away_team_id=away.id; match.start_time_utc=_parse_time(event.start_time_utc.value); match.status=str(event.status.value); match.retrieved_at=event.retrieved_at
    for market in event.markets:
        observed=_parse_time(market["last_update"]) if market.get("last_update") else event.retrieved_at
        for outcome in market.get("outcomes",[]):
            price=outcome.get("price")
            if not isinstance(price,(int,float)) or price<=1: continue
            session.add(OddsSnapshot(match_id=match.id,bookmaker_key=str(market.get("bookmaker_key") or market.get("bookmaker") or "unknown"),bookmaker_name=str(market.get("bookmaker") or "unknown"),market_key=str(market.get("market") or "unknown"),selection=str(outcome.get("name") or ""),point=outcome.get("point"),decimal_odds=float(price),observed_at=observed,retrieved_at=event.retrieved_at,source_url=f"https://api.theoddsapi.com/v4/sports/{event.payload.get('sport_key','soccer_epl')}/events/{event.event_id}/odds",raw={"outcome":outcome,"market":market}))
    return match
