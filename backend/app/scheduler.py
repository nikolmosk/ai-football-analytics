"""Lightweight APScheduler integration for periodic provider sync."""
from __future__ import annotations
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import get_odds_sync_interval_seconds

scheduler = AsyncIOScheduler()

def configure_scheduler(sync_callable) -> AsyncIOScheduler:
    scheduler.add_job(sync_callable, "interval", seconds=get_odds_sync_interval_seconds(),
                      id="football-odds-sync", replace_existing=True, max_instances=1,
                      coalesce=True, misfire_grace_time=30)
    return scheduler
