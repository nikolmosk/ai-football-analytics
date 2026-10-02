"""football-data.org v4 adapter for football fixtures/results.

Requires FOOTBALL_DATA_API_TOKEN. The adapter is intentionally server-side and
never exposes the token. It does not provide bookmaker odds or xG by itself.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import httpx

from app.providers.base import EventSnapshot, ProviderError, SourceRef, SourcedValue, SportsDataProvider


class FootballDataOrgProvider(SportsDataProvider):
    provider_name = "football-data.org"

    def __init__(
        self,
        token: str | None = None,
        *,
        base_url: str = "https://api.football-data.org/v4",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._token = token if token is not None else os.getenv("FOOTBALL_DATA_API_TOKEN")
        self._base_url = base_url.rstrip("/")
        self._client = client
        self._owns_client = client is None

    async def _request(self, path: str) -> dict[str, Any]:
        if not self._token:
            raise ProviderError("FOOTBALL_DATA_API_TOKEN is not configured")
        headers = {"X-Auth-Token": self._token, "Accept": "application/json"}
        try:
            if self._client is not None:
                response = await self._client.get(f"{self._base_url}{path}", headers=headers)
            else:
                async with httpx.AsyncClient(timeout=12.0) as client:
                    response = await client.get(f"{self._base_url}{path}", headers=headers)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise ProviderError("Provider returned an unexpected JSON shape")
            return payload
        except ProviderError:
            raise
        except (httpx.HTTPError, ValueError) as exc:
            raise ProviderError(f"football-data.org request failed: {type(exc).__name__}") from exc

    async def get_event(self, event_id: str) -> EventSnapshot:
        if not event_id.isdigit():
            raise ProviderError("football-data.org event_id must be a numeric match ID")
        payload = await self._request(f"/matches/{event_id}")
        now = datetime.now(timezone.utc)
        match_id = str(payload.get("id", event_id))
        competition = (payload.get("competition") or {}).get("name")
        start_time = payload.get("utcDate")
        status = payload.get("status")
        home = (payload.get("homeTeam") or {}).get("name")
        away = (payload.get("awayTeam") or {}).get("name")
        if not all((competition, start_time, status, home, away)):
            raise ProviderError("Provider response is missing one or more required match fields")

        source = SourceRef(
            provider=self.provider_name,
            source_id=match_id,
            url=f"https://www.football-data.org/match/{match_id}",
            retrieved_at=now,
            observed_at=_parse_timestamp(payload.get("lastUpdated")),
        )
        return EventSnapshot(
            event_id=match_id,
            sport="football",
            competition=SourcedValue(value=competition, status="VERIFIED", source=source),
            start_time_utc=SourcedValue(value=start_time, status="VERIFIED", source=source),
            status=SourcedValue(value=status, status="VERIFIED", source=source),
            participants=SourcedValue(value={"home": home, "away": away}, status="VERIFIED", source=source),
            markets=[],
            features={},
            payload={
                "season": payload.get("season"),
                "stage": payload.get("stage"),
                "matchday": payload.get("matchday"),
                "score": payload.get("score"),
                "venue": payload.get("venue"),
                "provider_last_updated": payload.get("lastUpdated"),
            },
            retrieved_at=now,
        )

    async def healthcheck(self) -> dict[str, str]:
        if not self._token:
            return {"provider": self.provider_name, "status": "NOT_CONFIGURED"}
        try:
            # Use a small, documented resource to verify credentials.
            await self._request("/competitions")
            return {"provider": self.provider_name, "status": "REACHABLE"}
        except ProviderError:
            return {"provider": self.provider_name, "status": "UNVERIFIED"}


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None
