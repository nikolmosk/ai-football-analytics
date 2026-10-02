from datetime import datetime, timedelta, timezone

from app.providers.base import EventSnapshot, SourceRef, SourcedValue
from app.services.data_quality import assess_event, check_sourced_value


NOW = datetime(2026, 10, 2, 12, 0, tzinfo=timezone.utc)


def sourced(value, *, status="VERIFIED", retrieved_at=NOW, ttl=3600):
    return SourcedValue(
        value=value,
        status=status,
        source=SourceRef(provider="test-fixture", retrieved_at=retrieved_at),
        valid_for_seconds=ttl,
    )


def test_sourced_value_can_be_verified_when_fresh():
    result = check_sourced_value("odds", sourced(2.1), NOW)
    assert result["status"] == "VERIFIED"
    assert result["issues"] == []


def test_stale_value_is_flagged():
    result = check_sourced_value(
        "odds", sourced(2.1, retrieved_at=NOW - timedelta(hours=2), ttl=60), NOW
    )
    assert result["status"] == "STALE"
    assert "stale" in result["issues"]


def test_event_without_critical_provenance_is_insufficient():
    event = EventSnapshot(
        event_id="fixture-1",
        sport="football",
        competition=SourcedValue(value="Example League", status="UNVERIFIED"),
        start_time_utc=SourcedValue(value=None, status="MISSING"),
        status=sourced("scheduled"),
        participants=sourced(["Home", "Away"]),
        retrieved_at=NOW,
    )
    result = assess_event(event, NOW)
    assert result["overall_status"] == "DATA INSUFFICIENT"
    assert "start_time_utc" in result["missing_or_unverified_critical_fields"]


def test_providerless_value_is_not_verified():
    result = check_sourced_value(
        "lineup", SourcedValue(value=["Player A"], status="VERIFIED"), NOW
    )
    assert result["status"] == "UNVERIFIED"
    assert "source_missing" in result["issues"]
