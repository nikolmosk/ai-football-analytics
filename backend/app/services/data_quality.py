"""Data-quality gates shared by all sport modules."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.providers.base import EventSnapshot, SourcedValue


def check_sourced_value(field_name: str, item: SourcedValue, now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    issues: list[str] = []
    status = item.status

    if item.value is None or status == "MISSING":
        issues.append("value_missing")
        status = "MISSING"
    if item.source is None:
        issues.append("source_missing")
        if status == "VERIFIED":
            status = "UNVERIFIED"
    if item.source is not None:
        if item.source.retrieved_at.tzinfo is None:
            issues.append("retrieval_timestamp_missing_timezone")
            status = "UNVERIFIED"
        if item.valid_for_seconds is not None:
            age = (now - item.source.retrieved_at).total_seconds()
            if age > item.valid_for_seconds:
                issues.append("stale")
                status = "STALE"

    return {"field": field_name, "status": status, "issues": issues}


def assess_event(snapshot: EventSnapshot, now: datetime | None = None) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for name, value in (
        ("competition", snapshot.competition),
        ("start_time_utc", snapshot.start_time_utc),
        ("status", snapshot.status),
        ("participants", snapshot.participants),
    ):
        checks.append(check_sourced_value(name, value, now))
    for name, value in snapshot.features.items():
        checks.append(check_sourced_value(name, value, now))

    critical = {"competition", "start_time_utc", "status", "participants"}
    missing_critical = [
        row["field"] for row in checks
        if row["field"] in critical and row["status"] in {"MISSING", "UNVERIFIED", "CONFLICT", "STALE"}
    ]
    issue_count = sum(bool(row["issues"]) for row in checks)
    if missing_critical:
        overall = "DATA INSUFFICIENT"
    elif issue_count:
        overall = "LIMITED"
    else:
        overall = "OK"
    return {
        "event_id": snapshot.event_id,
        "overall_status": overall,
        "checked_fields": len(checks),
        "issue_count": issue_count,
        "missing_or_unverified_critical_fields": missing_critical,
        "fields": checks,
        "note": "Quality status describes provenance/completeness, not predictive accuracy.",
    }
