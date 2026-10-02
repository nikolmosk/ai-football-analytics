# Development Roadmap

## Current state: alpha scaffold
- [x] Repository foundation and API health endpoint
- [x] Shared analytics system prompt and sport-specific prompts for CS2, Dota 2, major club football, NHL, NBA/EuroLeague
- [x] Deterministic decimal-odds, proportional de-vig, fair-odds and EV helpers
- [x] Initial independent-Poisson football score model
- [x] Unit tests for mathematical primitives
- [ ] Run CI and record test results
- [ ] Add API request/response schemas and endpoints for model helpers
- [ ] Add database migrations and persistent event/market snapshots
- [ ] Add provider interfaces with source timestamp and provenance requirements
- [ ] Add data-quality gates and stale-data policies
- [ ] Add virtual wallet, bet placement simulation and settlement ledger
- [ ] Add frontend/mobile integration
- [ ] Add backtesting, calibration, Brier score, log loss, ROI and CLV evaluation
- [ ] Add authentication and rate limiting before any hosted deployment

## Release gates
No real-data claim until a provider is configured and tested. No model described as calibrated until out-of-sample evaluation is recorded. No market may be shown as positive EV if data quality or settlement rules fail validation.
