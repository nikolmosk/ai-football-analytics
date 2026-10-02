# Data and provider policy

No live provider is configured in this repository yet. Data adapters must be added only after the provider's API terms, sport/competition coverage, licensing, rate limits, and odds rights are checked.

## Requirements for every observation
- Provider name and source identifier
- Retrieved timestamp in UTC
- Observation timestamp where available
- Explicit verification state
- Unit and time window for statistical features
- Market settlement rules and bookmaker/provider timestamp for odds
- Staleness policy appropriate to the field (odds and lineup statuses expire much faster than historical season aggregates)

Never commit API keys, personal tokens, licensed raw datasets, or production user data. Keep credentials in environment variables or a secret manager. Do not scrape sources contrary to their terms.

## Provider selection matrix (to be filled after evaluation)
| Sport | Fixtures/results | Statistics | Odds | Candidate | Status |
|---|---|---|---|---|---|
| Football (major club competitions) | TBD | TBD | TBD | Evaluate licensed APIs | Not connected |
| CS2 | TBD | TBD | TBD | Evaluate esports data APIs | Not connected |
| Dota 2 | TBD | TBD | TBD | Evaluate esports data APIs | Not connected |
| NHL | TBD | TBD | TBD | Evaluate licensed APIs | Not connected |
| NBA / EuroLeague | TBD | TBD | TBD | Evaluate licensed APIs | Not connected |

A provider's existence is not evidence that our application is connected to it. Update this file only after a working adapter and integration test are present.
