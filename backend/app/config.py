"""Environment configuration for the backend."""
from __future__ import annotations

import os


def get_odds_api_key() -> str | None:
    return os.getenv("THE_ODDS_API_KEY")


def get_odds_api_base_url() -> str:
    return os.getenv("THE_ODDS_API_BASE_URL", "https://api.theoddsapi.com")


def get_odds_api_sport() -> str:
    return os.getenv("THE_ODDS_API_SPORT", "soccer_epl")


def get_odds_api_regions() -> str:
    return os.getenv("THE_ODDS_API_REGIONS", "eu")


def get_odds_api_markets() -> str:
    return os.getenv("THE_ODDS_API_MARKETS", "h2h,totals,spreads")
