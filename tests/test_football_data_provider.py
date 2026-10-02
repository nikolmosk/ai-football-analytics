import asyncio
import json

import httpx
import pytest

from app.providers.base import ProviderError
from app.providers.football_data_org import FootballDataOrgProvider


MATCH = {
    "id": 12345,
    "utcDate": "2026-10-03T16:30:00Z",
    "status": "SCHEDULED",
    "lastUpdated": "2026-10-02T09:00:00Z",
    "competition": {"name": "Example Premier League"},
    "homeTeam": {"name": "Home FC"},
    "awayTeam": {"name": "Away FC"},
    "season": {"startDate": "2026-08-01"},
    "stage": "REGULAR_SEASON",
    "matchday": 7,
    "score": {"winner": None},
}


def test_adapter_normalizes_match_and_preserves_provenance():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v4/matches/12345"
        assert request.headers["X-Auth-Token"] == "test-token"
        return httpx.Response(200, json=MATCH)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = FootballDataOrgProvider("test-token", base_url="https://test.invalid/v4", client=client)
    try:
        event = asyncio.run(provider.get_event("12345"))
    finally:
        asyncio.run(client.aclose())

    assert event.event_id == "12345"
    assert event.sport == "football"
    assert event.competition.value == "Example Premier League"
    assert event.participants.value == {"home": "Home FC", "away": "Away FC"}
    assert event.competition.source.provider == "football-data.org"
    assert event.retrieved_at.tzinfo is not None


def test_adapter_rejects_non_numeric_id():
    provider = FootballDataOrgProvider("test-token")
    with pytest.raises(ProviderError):
        asyncio.run(provider.get_event("not-a-match-id"))


def test_adapter_does_not_call_provider_without_token():
    provider = FootballDataOrgProvider(token="")
    with pytest.raises(ProviderError, match="not configured"):
        asyncio.run(provider.get_event("12345"))
