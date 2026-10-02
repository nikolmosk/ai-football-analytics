# AI Football Analytics

Open-source football match analytics platform with a statistical prediction engine, fair-odds calculations, value-market analysis, and a virtual bankroll for paper trading.

> **Status:** early MVP scaffold. The current implementation is a development starter, not a production betting product. Any example data must be clearly labelled as demo data.

## Project principles

- Never invent match statistics, odds, lineups, injuries, referee information, weather, or results.
- Return `DATA INSUFFICIENT` or `UNVERIFIED` when required source data is missing.
- Keep model probability, market probability, fair odds, edge, expected value, confidence, and data quality separate.
- Virtual bets only; this project does not place real wagers.

## Repository layout

- `backend/` — FastAPI service and analytics primitives
- `mobile/` — planned React Native Android/iOS client
- `ml/` — planned model training and evaluation
- `data/` — data contracts and sample fixtures
- `docs/` — architecture and roadmap
- `tests/` — automated tests

## Quick start (backend)

Requires Python 3.12+.

```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for the API documentation.

## Safety and data quality

The starter exposes a health endpoint and deterministic mathematical helpers only. It does not yet connect to live football feeds or bookmaker APIs. Never treat demo data or unvalidated model output as a recommendation.

## Roadmap

1. Backend API and tests
2. Match and odds provider abstractions
3. Poisson probabilities and fair odds
4. Virtual bankroll and bet history
5. Mobile client
6. Model calibration, backtesting, and live-data integrations

## License

MIT — see [LICENSE](LICENSE).


## Sports prompt suite

The shared system prompt and sport-specific prompt files live in [`docs/prompts/`](docs/prompts/README.md). They cover CS2, Dota 2, major club football, NHL, and NBA/EuroLeague. They define strict source provenance, data-quality gates, market settlement checks, probability/EV semantics, and a structured JSON output contract.

## Analytics API (early alpha)

- `POST /api/v1/analytics/football/poisson` — derive regulation 1X2 and selected totals/BTTS probabilities from **caller-supplied expected goals**.
- `POST /api/v1/markets/binary` — fair odds, binary-market EV and optional probability edge.
- `POST /api/v1/markets/devig` — proportional de-vig for mutually exclusive outcomes.
- `POST /api/v1/analytics/probabilities/validate` — validate a 1X2 probability sum.

These endpoints are arithmetic/model primitives, not live predictions. They do not fetch real fixtures, statistics, or bookmaker prices. Outputs are marked unverified and the Poisson model is not calibrated. See [the roadmap](docs/roadmap.md) for the next milestones.
