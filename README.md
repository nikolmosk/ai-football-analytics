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
