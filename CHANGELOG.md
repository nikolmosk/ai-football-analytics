# Changelog

All notable changes to this project are documented here.

## v0.2.0 — Live Odds Foundation

### Added
- Server-side The Odds API v4 provider adapter.
- Normalized bookmaker and market payloads using the existing `EventSnapshot` contract.
- Provider healthcheck without exposing API credentials.
- Environment-based Odds API configuration.
- Explicit `NOT_CONFIGURED`, `REACHABLE`, and `UNVERIFIED` provider states.
- Example environment file containing no secrets.

### Changed
- The backend now has a concrete odds-provider implementation while keeping the provider abstraction intact.

### Safety / data quality
- API credentials are never returned by the backend.
- Live data is not labelled verified until the upstream request succeeds.
- No betting action or wager placement is implemented.

### Next
- v0.3.0: PostgreSQL models, migrations, matches and odds persistence.
