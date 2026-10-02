# Changelog

## v0.6.0 — Team Match Stats & Form Foundation

### Added
- Normalized `team_match_stats` PostgreSQL table with provenance, timestamps and nullable provider metrics.
- Idempotent repository persistence for team-match statistics.
- `GET /api/v1/matches/{id}/stats` for stored match statistics.
- `GET /api/v1/teams/{id}/form` with last-N form and all/home/away split.
- Optional `before_match_id` cutoff so form excludes the target match and all later matches.
- Form aggregation for W/D/L, points, goals, xG, shots, shots on target, possession and corners when source data exists.
- Tests for latest-N selection and missing-score handling.

### Data integrity
- No statistics are generated when a provider does not supply them.
- Missing values remain NULL rather than being estimated or invented.
- Form only consumes stored completed matches before the requested cutoff.
- xG remains unavailable until a verified stats provider supplies it.

### Provider status
- The Odds API remains the odds/event provider; it is not treated as a historical team-statistics provider.
- v0.6 establishes the normalized stats contract so a verified football statistics adapter can be added without changing the mobile API.

### Next
v0.7.0: verified football statistics ingestion adapter + automatic completed-match stats synchronization.
