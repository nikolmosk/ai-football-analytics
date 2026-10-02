"""Provider contracts for verified sports data.

Concrete integrations must attach provenance and observation timestamps. This
module intentionally performs no network calls and contains no API credentials.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SourceRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str = Field(min_length=1)
    source_id: str | None = None
    url: str | None = None
    retrieved_at: datetime
    observed_at: datetime | None = None


class SourcedValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: Any = None
    status: str = Field(pattern="^(VERIFIED|UNVERIFIED|MISSING|STALE|CONFLICT)$")
    source: SourceRef | None = None
    unit: str | None = None
    valid_for_seconds: int | None = Field(default=None, ge=0)


class EventSnapshot(BaseModel):
    """Normalized event envelope; sport-specific details stay in payload."""

    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(min_length=1)
    sport: str = Field(pattern="^(football|cs2|dota2|nhl|basketball)$")
    competition: SourcedValue
    start_time_utc: SourcedValue
    status: SourcedValue
    participants: SourcedValue
    markets: list[dict[str, Any]] = Field(default_factory=list)
    features: dict[str, SourcedValue] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)
    retrieved_at: datetime


class ProviderError(RuntimeError):
    """Raised when an upstream provider cannot return a usable response."""


class SportsDataProvider(ABC):
    """Minimal async interface implemented by each real provider adapter."""

    provider_name: str

    @abstractmethod
    async def get_event(self, event_id: str) -> EventSnapshot:
        """Fetch and normalize one event; raise ProviderError on failure."""

    @abstractmethod
    async def healthcheck(self) -> dict[str, str]:
        """Return provider configuration/health without leaking credentials."""
