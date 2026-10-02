from datetime import datetime, timezone
import httpx
import pytest

from app.providers.the_odds_api import TheOddsAPIProvider


@pytest.mark.asyncio
async def test_get_events_normalizes_provider_feed():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["x-api-key"] == "test-key"
        assert request.url.path.endswith("/v4/sports/soccer_epl/odds")
        return httpx.Response(200, json=[{
            "id": "evt-1",
            "sport_key": "soccer_epl",
            "sport_title": "English Premier League",
            "commence_time": "2026-10-03T14:00:00Z",
            "home_team": "Home FC",
            "away_team": "Away FC",
            "bookmakers": [{
                "key": "book",
                "title": "Book",
                "markets": [{
                    "key": "h2h",
                    "last_update": "2026-10-02T18:00:00Z",
                    "outcomes": [
                        {"name": "Home FC", "price": 2.1},
                        {"name": "Away FC", "price": 3.2},
                    ],
                }],
            }],
        ])

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = TheOddsAPIProvider(api_key="test-key", client=client)
        events = await provider.get_events()

    assert len(events) == 1
    assert events[0].event_id == "evt-1"
    assert events[0].competition.value == "soccer_epl"
    assert events[0].participants.value == {"home": "Home FC", "away": "Away FC"}
    assert events[0].markets[0]["bookmaker_key"] == "book"


@pytest.mark.asyncio
async def test_get_events_requires_key():
    provider = TheOddsAPIProvider(api_key=None)
    with pytest.raises(Exception, match="THE_ODDS_API_KEY"):
        await provider.get_events()
