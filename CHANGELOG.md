# Changelog

## v0.3.0 — PostgreSQL Persistence

### Added
- SQLAlchemy async database configuration.
- PostgreSQL models for competitions, teams, matches and odds snapshots.
- Alembic configuration and initial migration.
- Persistence repository for normalized The Odds API events.
- Odds are stored as observations, preserving line history.

### Data quality
- Provider event IDs remain linked to their source provider.
- Match and odds records retain retrieval and observation timestamps.
- Raw normalized market data is retained for auditability.
- No credentials or live secrets are stored in the repository.

### Next
v0.4.0: competitions, seasons, teams and normalized match ingestion.
