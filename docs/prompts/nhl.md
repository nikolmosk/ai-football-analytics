# Sport Prompt — NHL Ice Hockey

Append this after `master-sports-analytics.md`.

## Scope
Analyze NHL games only. Verify game ID, scheduled puck drop, status, home/away, regular season vs playoffs, and whether a market includes overtime and shootout.

## Required data
- Confirmed or projected starting goalie with source and timestamp; clearly distinguish confirmed from projected.
- Team/player results and metrics over stated windows: goals, shots, expected goals if provider methodology is known, scoring chances, special teams, penalty kill, power play, faceoffs if relevant, and opponent strength.
- Goalie save percentage / goals saved above expected only with sample size and source.
- Rest, back-to-back status, travel/time-zone changes, schedule density, and home advantage when supplied.
- Injuries and line combinations only with verified status and timestamp.
- Odds, puck line, totals, moneyline, player props, settlement rules including regulation vs full game.

## Analysis logic
- Starting goalie status is often material. If it is unknown, either increase uncertainty and limit markets or mark goalie-sensitive markets `DATA INSUFFICIENT` according to the model's data gate.
- Separate regulation 3-way markets from full-game moneyline markets that include overtime/shootout.
- Model expected scoring and win probabilities with a validated method; account for overdispersion/low-scoring effects if the implementation supports them.
- Evaluate power play and penalty kill only using comparable sample windows and opponent context.
- Do not infer goalie starts, injuries, line combinations, fatigue, or travel effects from team reputation.
- Small goalie samples, backup starts, recent trades, roster changes, and special-team variance should be reflected in uncertainty.
- Never confuse a regulation tie with the final game winner.

## Market handling
Support moneyline, regulation 3-way, puck line, totals, and player props only with market-specific models and settlement rules. Player props require confirmed participation, exact lines, and a dedicated statistical distribution.

## Sport-specific output additions
Include:
- `goalie_status_home`, `goalie_status_away`, `game_scope`, `overtime_included`;
- `special_teams_data_quality`, `rest_travel_data_quality`;
- supporting factors: goalie evidence, team chance metrics, special teams, schedule context;
- counterarguments: goalie uncertainty, small samples, special-team variance, market settlement differences.

If the goalie or overtime scope is unknown, explicitly flag it and avoid false precision.
