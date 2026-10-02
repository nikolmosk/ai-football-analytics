# Sports Betting Analytics Prompt Suite

This folder contains a reusable instruction system for pre-match analysis in five sports:
- Counter-Strike 2 (CS2)
- Dota 2
- Association football (major club competitions)
- NHL ice hockey
- Basketball (NBA and EuroLeague)

## How to use
1. Supply the **shared system prompt** in `master-sports-analytics.md`.
2. Append exactly one sport-specific prompt for the sport and competition being analyzed.
3. Pass a structured data packet from verified providers. Keep source, retrieval time, event start time, market line, odds, and settlement rules attached to each field.
4. Require machine-readable JSON first; render prose only from the resulting verified JSON.
5. Store the model version and data snapshot so every forecast can be audited later.

## Non-negotiable data policy
A prompt cannot create missing data. Do not ask an LLM to browse its memory for current rosters, odds, injuries, maps, lineups, or results. Data must arrive from configured providers or be explicitly marked `UNVERIFIED`. If a critical field is missing, return `DATA INSUFFICIENT` for affected markets.

## Files
- `master-sports-analytics.md` — shared role, data contract, probability and EV definitions, JSON output contract.
- `cs2.md` — maps, veto, side, economy, player/team metrics and esports market settlement.
- `dota2.md` — draft, lanes, patch, objectives, player roles and map/series markets.
- `football.md` — major club competitions, 1X2, totals, BTTS, Asian handicap, xG and squad context.
- `nhl.md` — NHL, goalie confirmation, rest/travel, special teams, puck line and totals.
- `basketball-nba-euroleague.md` — NBA and EuroLeague, pace, ratings, availability, spread and totals.

## Versioning
Treat these prompts as versioned product logic. Any change to probability definitions, data gates, or market settlement requires tests and a version bump. Prompts are not substitutes for statistical models, calibration, backtesting, or provider contracts.
