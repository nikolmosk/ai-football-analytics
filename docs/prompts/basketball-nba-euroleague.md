# Sport Prompt — Basketball (NBA and EuroLeague)

Append this after `master-sports-analytics.md`.

## Scope
Only analyze NBA and EuroLeague events selected in configuration. Confirm competition, season, game ID, scheduled tip-off, status, home/away, and whether the game is regular season, playoffs, or another stage.

## Required data
- Player availability/injury status with source, timestamp, and status vocabulary; confirmed starting lineup when available.
- Team/player stats with defined windows and sample sizes: offensive/defensive rating, net rating, pace, eFG%, turnover rate, offensive rebound rate, free-throw rate, shot profile, transition efficiency and lineup/on-off data where available.
- Opponent strength, home court, rest days, back-to-back, travel, time-zone changes, schedule density.
- NBA-specific: official injury report status and rotation availability when supplied.
- EuroLeague-specific: competition-specific roster/rotation, home-court context, schedule density, and differences in pace/stat collection. Do not transfer NBA priors without validated adaptation.
- Odds and settlement rules for moneyline, spread/handicap, totals, team totals, quarters/halves, and player props.

## Analysis logic
- Model game scoring and margin with a method validated separately for NBA and EuroLeague. Do not assume one league's parameters/calibration apply to the other.
- Use possessions/pace and efficiency estimates when reliable. Adjust for opponent quality, home court, rest and lineup availability only through supported features.
- Injury impact must be based on verified status and an explicit impact method; do not assign an invented point value to a player absence.
- Separate full-game markets from quarter/half markets; player props need a dedicated minutes/usage and outcome model.
- Handle overtime explicitly: many full-game totals/spreads include OT, while period markets do not; use the actual settlement rules.
- Small samples, late scratches, minutes restrictions, rotation changes, three-point variance, foul trouble and EuroLeague/NBA schedule differences increase uncertainty.
- Never invent injury reports, starting fives, minutes limits, or odds.

## Market handling
Support moneyline, point spread, totals, team totals, periods and player props only if a market-specific distribution and settlement-aware EV calculation exist. For spreads/totals with pushes or integer lines, account for push probability rather than applying a simple binary formula.

## Sport-specific output additions
Include:
- `league`, `lineup_status`, `availability_snapshot_time`, `model_league_calibration`;
- `pace_estimate`, `expected_points_home`, `expected_points_away`, `margin_distribution_reference`;
- supporting factors: lineup status, efficiency, pace, rest/travel if verified;
- counterarguments: availability uncertainty, three-point variance, minutes/rotation risk, league-specific calibration;
- exact overtime and push settlement treatment.

If league-specific calibration is not available, label estimates unverified and do not present them as calibrated probabilities.
