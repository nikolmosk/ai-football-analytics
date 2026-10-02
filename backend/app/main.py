"""FastAPI application for AI Football Analytics."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.analytics.football_poisson import outcome_probabilities
from app.analytics.markets import (
    devig_proportional,
    edge_percentage_points,
    expected_value_per_unit,
    fair_decimal_odds,
)
from app.config import (
    get_odds_api_base_url,
    get_odds_api_key,
    get_odds_api_markets,
    get_odds_api_regions,
    get_odds_api_sport,
)
from app.providers.base import ProviderError
from app.providers.registry import ProviderRegistry
from app.providers.the_odds_api import TheOddsAPIProvider

provider_registry = ProviderRegistry()
odds_provider = TheOddsAPIProvider(
    api_key=get_odds_api_key(),
    base_url=get_odds_api_base_url(),
    sport=get_odds_api_sport(),
    regions=get_odds_api_regions(),
    markets=get_odds_api_markets(),
)
provider_registry.register("football", odds_provider)

app = FastAPI(
    title="AI Football Analytics API",
    version="0.2.0",
    description="Football analytics backend with server-side bookmaker odds integration.",
)

class ProbabilityRequest(BaseModel):
    home: float = Field(ge=0, le=1)
    draw: float = Field(ge=0, le=1)
    away: float = Field(ge=0, le=1)

class FootballPoissonRequest(BaseModel):
    home_xg: float = Field(ge=0, le=10)
    away_xg: float = Field(ge=0, le=10)
    max_goals: int = Field(default=12, ge=1, le=30)

class BinaryMarketRequest(BaseModel):
    model_probability: float = Field(ge=0, le=1)
    decimal_odds: float = Field(gt=1)
    market_probability_devig: float | None = Field(default=None, ge=0, le=1)

class DevigRequest(BaseModel):
    decimal_odds: list[float] = Field(min_length=2)

@app.get("/api/v1/data/providers")
def data_provider_status() -> dict[str, object]:
    return provider_registry.status()

@app.get("/api/v1/data/providers/football/health")
async def football_provider_health() -> dict[str, str]:
    return await odds_provider.healthcheck()

@app.get("/api/v1/data/football/events/{event_id}")
async def football_event(event_id: str) -> dict[str, object]:
    try:
        snapshot = await odds_provider.get_event(event_id)
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return snapshot.model_dump(mode="json")

@app.get("/health")
async def health() -> dict[str, str]:
    provider = await odds_provider.healthcheck()
    return {"status": "ok", "data_mode": "live_provider_configured", "odds_provider": provider["status"]}

@app.get("/")
def root() -> dict[str, str]:
    return {"name": "AI Football Analytics API", "version": "0.2.0", "status": "development", "data_status": "SOURCE_GATED"}

@app.post("/api/v1/analytics/probabilities/validate")
def validate_probabilities(payload: ProbabilityRequest) -> dict[str, object]:
    total = payload.home + payload.draw + payload.away
    valid = abs(total - 1.0) <= 0.01
    return {"valid": valid, "sum": round(total, 6), "message": "Probabilities sum to approximately 1." if valid else "DATA INSUFFICIENT: probabilities must sum to approximately 1."}

@app.post("/api/v1/analytics/football/poisson")
def football_poisson(payload: FootballPoissonRequest) -> dict[str, object]:
    result = outcome_probabilities(payload.home_xg, payload.away_xg, payload.max_goals)
    result["input_status"] = "CALLER_SUPPLIED_UNVERIFIED"
    result["warning"] = "Expected-goal inputs were supplied by the caller; no match data was fetched. The model is not calibrated and the score matrix is truncated."
    return result

@app.post("/api/v1/markets/binary")
def binary_market(payload: BinaryMarketRequest) -> dict[str, float | None | str]:
    probability = payload.model_probability
    fair_odds = fair_decimal_odds(probability)
    ev = expected_value_per_unit(probability, payload.decimal_odds)
    edge = edge_percentage_points(probability, payload.market_probability_devig) if payload.market_probability_devig is not None else None
    return {"model_probability": probability, "decimal_odds": payload.decimal_odds, "fair_decimal_odds": fair_odds if fair_odds != float("inf") else None, "expected_value_per_unit": ev, "edge_percentage_points": edge, "status": "UNVERIFIED", "warning": "Arithmetic only; input probability and market equivalence are not verified."}

@app.post("/api/v1/markets/devig")
def devig_market(payload: DevigRequest) -> dict[str, object]:
    probabilities = devig_proportional(payload.decimal_odds)
    return {"method": "proportional", "decimal_odds": payload.decimal_odds, "market_probabilities": probabilities, "sum": sum(probabilities), "status": "UNVERIFIED", "warning": "Inputs must be mutually exclusive outcomes from the same market snapshot."}
