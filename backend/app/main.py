"""Minimal API scaffold for AI Football Analytics."""

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="AI Football Analytics API",
    version="0.1.0-alpha",
    description=(
        "Early development API. No live data providers are configured; "
        "missing inputs must remain explicitly unverified."
    ),
)


class ProbabilityRequest(BaseModel):
    home: float = Field(ge=0, le=1, description="Model probability for home win")
    draw: float = Field(ge=0, le=1, description="Model probability for draw")
    away: float = Field(ge=0, le=1, description="Model probability for away win")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "data_mode": "demo_only"}


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "AI Football Analytics API",
        "version": "0.1.0-alpha",
        "status": "development scaffold",
        "data_status": "UNVERIFIED",
    }


@app.post("/api/v1/analytics/probabilities/validate")
def validate_probabilities(payload: ProbabilityRequest) -> dict[str, object]:
    total = payload.home + payload.draw + payload.away
    valid = abs(total - 1.0) <= 0.01
    return {
        "valid": valid,
        "sum": round(total, 6),
        "message": "Probabilities sum to approximately 1." if valid else (
            "DATA INSUFFICIENT: probabilities must sum to approximately 1."
        ),
    }
