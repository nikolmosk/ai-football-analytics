# Changelog

## v0.4.0 — Normalized Match Ingestion

### Added
- The Odds API event-list ingestion through the football odds feed.
- PostgreSQL `seasons` entity linked to competitions and matches.
- Normalized match list/detail endpoints with pagination and status filtering.
- Match odds history endpoint with observation timestamps.
- `POST /api/v1/data/football/sync` to ingest the current provider feed server-side.
- Provider source URLs and retrieval timestamps retained for auditability.
- Automated provider normalization tests using `httpx.MockTransport`.

### Data quality
- API credentials remain server-side in environment configuration.
- The provider event ID remains the stable external identity for matches.
- Season records use an explicit `current` provider-feed bucket because The Odds API event payload does not supply a verified season identifier in this adapter; no invented competition season label is exposed.
- Odds point values are normalized into a deterministic `point_key`, avoiding PostgreSQL NULL uniqueness gaps.

### API
- `GET /api/v1/matches`
- `GET /api/v1/matches/{id}`
- `GET /api/v1/matches/{id}/odds`
- `POST /api/v1/data/football/sync`

### Next
v0.5.0: scheduled odds ingestion, snapshot deduplication and background jobs.
