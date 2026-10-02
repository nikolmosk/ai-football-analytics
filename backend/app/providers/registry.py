"""Explicit provider registry.

No provider is registered by default: the app must not imply live data is
available until an adapter has been configured and health-checked.
"""
from __future__ import annotations

from app.providers.base import SportsDataProvider


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, SportsDataProvider] = {}

    def register(self, sport: str, provider: SportsDataProvider) -> None:
        if sport not in {"football", "cs2", "dota2", "nhl", "basketball"}:
            raise ValueError(f"unsupported sport: {sport}")
        self._providers[sport] = provider

    def get(self, sport: str) -> SportsDataProvider | None:
        return self._providers.get(sport)

    def configured_sports(self) -> list[str]:
        return sorted(self._providers.keys())

    def status(self) -> dict[str, object]:
        return {
            "live_data_enabled": bool(self._providers),
            "configured_sports": self.configured_sports(),
            "status": "UNVERIFIED" if self._providers else "DATA INSUFFICIENT",
        }
