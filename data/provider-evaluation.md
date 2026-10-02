# Provider evaluation (initial research)

**Status: candidates only. Nothing in this table means an integration is active.** Check contract, plan, data rights, rate limits, coverage, and commercial-use terms before enabling a provider in production.

| Need | Candidate | What current public documentation supports | Limitations / next check |
|---|---|---|---|
| Major club football fixtures/results | [football-data.org](https://www.football-data.org/) | Its documented v4 API provides competition, match, team, standings and scorer resources. The published coverage page lists major competitions including Champions League, Premier League, Bundesliga, Ligue 1, Serie A and La Liga. | Do not assume every competition, xG, lineups, injuries or bookmaker odds are available on the chosen plan. Confirm exact competition/field coverage and terms. |
| CS2 and Dota 2 esports stats | [PandaScore](https://www.pandascore.co/) | Public product material describes CS and Dota 2 esports data, fixtures and statistics. | Stats and third-party bookmaker odds are separate products; its FAQ says stats API does not include third-party bookmaker odds. Confirm contract/plan and required historical/live endpoints. |
| NHL schedules and official game data | [NHL API / NHL.com](https://www.nhl.com/) | Candidate source for official league game and team information. | No adapter has been implemented or tested; confirm current public endpoint stability, usage terms, and access to goalie confirmations / advanced stats. |
| NBA schedule and stats | [NBA Stats](https://www.nba.com/stats) | Candidate source for league schedules and statistics. | Confirm API availability, permitted use, reliability, and licensing before integration; do not depend on undocumented endpoints for a production service. |
| EuroLeague | [EuroLeague](https://www.euroleaguebasketball.net/) | Official competition source to evaluate for schedule and statistics. | Verify API/feed access, rights and historical coverage; no adapter active. |
| Odds across sports | Licensed odds provider to be selected | Odds must include bookmaker, decimal price, market/selection/line, update timestamp and settlement rules. | Provider selection must cover the desired competitions and markets and explicitly permit intended use. Never scrape or redistribute without rights. |

## Integration order

1. Choose a source for football fixtures/results and request an API key.
2. Build and test a server-side adapter using an environment variable such as `FOOTBALL_DATA_API_TOKEN`.
3. Add an odds source only after checking market coverage and licensing.
4. Evaluate PandaScore separately for esports stats and odds.
5. Evaluate hockey and basketball sources and verify coverage before implementing adapters.
6. Add contract tests and freshness thresholds for every provider.

## Current truthful status

- Live providers configured: **none**
- Real odds feed configured: **none**
- Real fixtures/statistics in application: **none**
- All current mathematical endpoints: caller-supplied inputs only, unverified.
