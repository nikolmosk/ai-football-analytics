import httpx
import pytest

from app.providers.the_odds_api import TheOddsAPIProvider


@pytest.mark.asyncio
async def test_the_odds_api_normalizes_event_and_markets():
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["x-api-key"] == "test-key"
        return httpx.Response(
            200,
            json={
                "id": "event-1",
                "sport_key": "soccer_epl",
                "sport_title": "EPL",
                "commence_time": "2026-10-03T18:00:00Z",
                "home_team": "Home FC",
                "away_team": "Away FC",
                "bookmakers": [
                    {
                        "key": "demo_book",
                        "title": "Demo Book",
                        "markets": [
                            {
                                "key": "h2h",
                                "last_update": "2026-10-03T17:00:00Z",
                                "outcomes": [
                                    {"name": "Home FC", "price": 2.1},
                                    {"name": "Away FC", "price": 3.2},
                                    {"name": "Draw", "price": 3.4},
                                ],
                            }
                        ],
                    }
                ],
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = TheOddsAPIProvider(api_key="test-key", client=client)
        event = await provider.get_event("event-1")

    assert event.event_id == "event-1"
    assert event.participants.value == {"home": "Home FC", "away": "Away FC"}
    assert event.markets[0]["bookmaker"] == "Demo Book"
    assert event.markets[0]["market"] == "h2h"
    assert event.markets[0]["outcomes"][0]["price"] == 2.1


@pytest.mark.asyncio
async def test_the_odds_api_requires_key():
    provider = TheOddsAPIProvider(api_key=None)
    with pytest.raises(RuntimeError, match="THE_ODDS_API_KEY"):
        await provider.get_event("event-1")
