# Changelog

## v0.5.0 — Scheduled Odds Ingestion

### Added
- Dedicated server-side odds ingestion service.
- APScheduler interval job for automatic odds refresh.
- Redis distributed lock so multiple API instances do not run the same sync simultaneously.
- Redis health status in `/health`.
- Configurable `ODDS_SYNC_INTERVAL_SECONDS` with a 30-second safety floor.
- Configurable `REDIS_URL`.
- Snapshot-level deduplication by match, bookmaker, market, selection, point and observation timestamp.

### API
- `POST /api/v1/data/football/sync` now uses the shared ingestion service.
- `/health` reports provider and Redis availability.

### Data integrity
- Repeated provider observations are not inserted twice.
- Scheduler failures do not invent fallback odds.
- Provider credentials remain server-side.

### Next
v0.6.0: normalized team-match statistics and form history.
