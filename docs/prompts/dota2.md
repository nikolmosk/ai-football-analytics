# Sport Prompt — Dota 2

Append this after `master-sports-analytics.md`.

## Scope
Analyze the specified Dota 2 event and market using verified tournament, patch, series-format, roster, and statistics data. Confirm whether the market concerns one game or the entire series.

## Required data
- Event ID, tournament/stage, scheduled time/status, BO format, series score if live data is explicitly supported.
- Verified active roster, role assignments, stand-ins, substitutions, and player identity mapping.
- Patch/version at match time, tournament rules, draft status, pick/ban sequence and side assignment when available.
- Team/player statistics with sample sizes and opponent context: game win rate, lane outcomes, net worth and experience at fixed minutes, first blood/tower/Roshan, objective conversion, game duration, comeback rate, draft win rates, and performance by patch.
- Market lines, decimal odds, timestamps, game/series scope, settlement rules.

## Analysis logic
- Treat draft and patch as high-impact variables. Before draft completion, explicitly state draft uncertainty; do not infer heroes or bans.
- Evaluate lane matchups, draft execution, scaling, teamfight initiation, objective control, vision, Roshan control, and ability to close games only where supported by supplied features.
- Separate game-level probability from series probability. Compute series probability using game-level estimates and the actual format only when assumptions about map/game independence are stated and justified.
- Account for side selection, roster/role changes, patch shifts, opponent strength, and sample-size limitations.
- Do not use a team's aggregate win rate without patch, opponent, and format context where those factors are material.
- Never invent draft picks, bans, player roles, patch notes, odds, or injuries/availability.

## Market handling
Analyze only supplied markets: match/series winner, game winner, map/game handicap, total games, game duration, first objective, or player props. Props require confirmed player participation, exact market definitions, and settlement rules. Markets tied to draft should be provisional before draft and recalculated when verified picks arrive.

## Sport-specific output additions
Include:
- `patch_status`, `roster_status`, `draft_status`, `side_assignment_status`;
- `game_vs_series_scope`;
- supporting factors: patch-adjusted data, lane/draft interactions, objective control, role continuity;
- counterarguments: draft uncertainty, patch shift, small sample, lineup changes, game-to-game dependence;
- sensitivity to draft completion and side selection.

If a key draft, roster, or patch field is missing, mark the affected market `DATA INSUFFICIENT` or `UNVERIFIED`.
