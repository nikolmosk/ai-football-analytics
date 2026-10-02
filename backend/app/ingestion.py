"""Server-side football odds ingestion service."""
from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.providers.base import ProviderError
from app.providers.the_odds_api import TheOddsAPIProvider
from app.repositories import persist_events

async def sync_odds(provider: TheOddsAPIProvider, session: AsyncSession) -> dict[str, object]:
    started = datetime.now(timezone.utc)
    events = await provider.get_events()
    persisted = await persist_events(session, events, provider=provider.provider_name)
    return {"provider": provider.provider_name, "events_seen": len(events), "events_persisted": persisted,
            "started_at": started.isoformat(), "completed_at": datetime.now(timezone.utc).isoformat()}

async def safe_sync_odds(provider: TheOddsAPIProvider, session: AsyncSession) -> dict[str, object]:
    try:
        return await sync_odds(provider, session)
    except ProviderError:
        await session.rollback()
        raise
