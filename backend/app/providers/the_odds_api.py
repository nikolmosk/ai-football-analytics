"""The Odds API v4 adapter for football odds.

The API key is read only from server-side configuration and is never returned
by this adapter. The adapter normalizes bookmaker/outcome payloads into the
project's EventSnapshot contract.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.providers.base import EventSnapshot, ProviderError, SourceRef, SourcedValue, SportsDataProvider


class TheOddsAPIProvider(SportsDataProvider):
    provider_name = "the-odds-api"

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = "https://api.theoddsapi.com",
        sport: str = "soccer_epl",
        regions: str = "eu",
        markets: str = "h2h,totals,spreads",
        timeout: float = 15.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._sport = sport
        self._regions = regions
        self._markets = markets
        self._timeout = timeout
        self._client = client

    async def _request(self, path: str, params: dict[str, str] | None = None) -> Any:
        if not self._api_key:
            raise ProviderError("THE_ODDS_API_KEY is not configured")

        headers = {"x-api-key": self._api_key, "Accept": "application/json"}
        try:
            if self._client is not None:
                response = await self._client.get(
                    f"{self._base_url}{path}",
                    headers=headers,
                    params=params,
                )
            else:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.get(
                        f"{self._base_url}{path}",
                        headers=headers,
                        params=params,
                    )
            response.raise_for_status()
            return response.json()
        except ProviderError:
            raise
        except httpx.HTTPStatusError as exc:
            raise ProviderError(
                f"The Odds API returned HTTP {exc.response.status_code}"
            ) from exc
        except (httpx.HTTPError, ValueError) as exc:
            raise ProviderError(
                f"The Odds API request failed: {type(exc).__name__}"
            ) from exc

    async def get_event(self, event_id: str) -> EventSnapshot:
        payload = await self._request(
            f"/v4/sports/{self._sport}/events/{event_id}/odds",
            {
                "regions": self._regions,
                "markets": self._markets,
                "oddsFormat": "decimal",
            },
        )
        if not isinstance(payload, dict):
            raise ProviderError("The Odds API returned an unexpected event payload")

        now = datetime.now(timezone.utc)
        home = payload.get("home_team")
        away = payload.get("away_team")
        commence = payload.get("commence_time")
        if not all((payload.get("id"), home, away, commence)):
            raise ProviderError("The Odds API event is missing required fields")

        source = SourceRef(
            provider=self.provider_name,
            source_id=str(payload["id"]),
            url=f"{self._base_url}/v4/sports/{self._sport}/events/{event_id}/odds",
            retrieved_at=now,
            observed_at=_parse_timestamp(payload.get("commence_time")),
        )

        return EventSnapshot(
            event_id=str(payload["id"]),
            sport="football",
            competition=SourcedValue(
                value=self._sport,
                status="VERIFIED",
                source=source,
            ),
            start_time_utc=SourcedValue(
                value=commence,
                status="VERIFIED",
                source=source,
            ),
            status=SourcedValue(value="scheduled", status="VERIFIED", source=source),
            participants=SourcedValue(
                value={"home": home, "away": away},
                status="VERIFIED",
                source=source,
            ),
            markets=_normalize_bookmakers(payload.get("bookmakers", [])),
            payload={
                "sport_key": payload.get("sport_key"),
                "sport_title": payload.get("sport_title"),
                "bookmakers_count": len(payload.get("bookmakers", [])),
            },
            retrieved_at=now,
        )

    async def healthcheck(self) -> dict[str, str]:
        if not self._api_key:
            return {"provider": self.provider_name, "status": "NOT_CONFIGURED"}
        try:
            payload = await self._request("/v4/sports")
            return {
                "provider": self.provider_name,
                "status": "REACHABLE" if isinstance(payload, list) else "UNVERIFIED",
            }
        except ProviderError:
            return {"provider": self.provider_name, "status": "UNVERIFIED"}


def _normalize_bookmakers(bookmakers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    markets: list[dict[str, Any]] = []
    for bookmaker in bookmakers:
        name = bookmaker.get("title") or bookmaker.get("key")
        for market in bookmaker.get("markets", []):
            outcomes = []
            for outcome in market.get("outcomes", []):
                outcomes.append(
                    {
                        "name": outcome.get("name"),
                        "price": outcome.get("price"),
                        "point": outcome.get("point"),
                    }
                )
            markets.append(
                {
                    "bookmaker": name,
                    "bookmaker_key": bookmaker.get("key"),
                    "market": market.get("key"),
                    "last_update": market.get("last_update"),
                    "outcomes": outcomes,
                }
            )
    return markets


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None
