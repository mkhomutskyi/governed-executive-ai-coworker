"""Validate governed evidence and the decision contract in an executive Monday brief.

Usage: python check_brief.py brief.md kpis.json

The JSON file can contain two weekly metric-view rows for table-only validation.
For full validation, use an object with `weekly` and `regional` row lists.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

ROWS = {
    "Pipeline created": ("pipeline_created", "relative"),
    "Bookings": ("bookings", "relative"),
    "Bookings target": ("bookings_target", "relative"),
    "Bookings attainment": ("bookings_attainment", "points"),
    "Recognized revenue": ("recognized_revenue", "relative"),
    "Revenue attainment": ("revenue_attainment", "points"),
    "Marketing spend": ("marketing_spend", "relative"),
    "Marketing-sourced pipeline": ("marketing_sourced_pipeline", "relative"),
    "Pipeline per marketing dollar": ("pipeline_per_marketing_dollar", "relative"),
    "Qualified leads": ("qualified_leads", "relative"),
    "Cost per qualified lead": ("cost_per_qualified_lead", "relative"),
    "Win rate": ("win_rate", "points"),
}

RATE_FIELDS = {"bookings_attainment", "revenue_attainment", "win_rate"}


def parse_number(cell: str) -> float | None:
    normalized = cell.replace("\u2212", "-").replace("−", "-")
    normalized = re.sub(r"\bper\s+\$?1\b", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"percentage\s+points?|\bpp\b", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"[,$%+\s]", "", normalized)
    if normalized in {"", "-", "n/a", "N/A"}:
        return None
    return float(normalized)


def normalize_evidence(raw: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if isinstance(raw, list):
        return raw, []
    if not isinstance(raw, dict):
        raise ValueError("kpis.json must be a weekly row list or an evidence object")
    weekly = raw.get("weekly")
    regional = raw.get("regional", [])
    if not isinstance(weekly, list) or not isinstance(regional, list):
        raise ValueError("evidence object must contain weekly and regional row lists")
    return weekly, regional


def normalize_rows(raw: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    rows, _ = normalize_evidence(raw)
    if len(rows) != 2:
        raise ValueError("kpis.json must contain exactly two weekly metric-view rows")
    rows = sorted(rows, key=lambda row: str(row.get("week") or row.get("Week")))
    prior, current = rows
    prior_week = date.fromisoformat(str(prior.get("week") or prior.get("Week"))[:10])
    current_week = date.fromisoformat(str(current.get("week") or current.get("Week"))[:10])
    if current_week - prior_week != timedelta(days=7):
        raise ValueError("KPI rows must be consecutive Monday weeks")
    if prior_week.weekday() != 0 or current_week.weekday() != 0:
        raise ValueError("Both KPI weeks must start on Monday")
    return prior, current


def displayed_value(field: str, row: dict[str, Any]) -> float:
    value = float(row[field])
    return value * 100 if field in RATE_FIELDS else value


def expected_change(field: str, mode: str, prior: dict[str, Any], current: dict[str, Any]) -> float:
    prior_value = float(prior[field])
    current_value = float(current[field])
    if mode == "points":
        return (current_value - prior_value) * 100
    if prior_value == 0:
        raise ValueError(f"Cannot calculate relative change for zero prior value: {field}")
    return (current_value - prior_value) / prior_value * 100


def close_enough(actual: float | None, expected: float, percentage: bool) -> bool:
    if actual is None:
        return False
    tolerance = 0.06 if percentage else max(1.0, abs(expected) * 0.0006)
    return abs(actual - expected) <= tolerance


def section(brief: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^{re.escape(heading)}\s*$\n(.*?)(?=^##?\s|\Z)",
        brief,
    )
    return match.group(1) if match else ""


def require_markers(content: str, label: str, markers: list[str]) -> list[str]:
    return [f"{label}: missing governed value {marker!r}" for marker in markers if marker not in content]


def check_narrative(
    brief: str,
    prior: dict[str, Any],
    current: dict[str, Any],
    regional: list[dict[str, Any]],
) -> list[str]:
    if not regional:
        return []

    errors: list[str] = []
    headline = section(brief, "## Headline")
    changed = section(brief, "## What changed")
    decisions = section(brief, "## Three decisions for Monday")

    bookings_change = expected_change("bookings", "relative", prior, current)
    attainment_change = expected_change("bookings_attainment", "points", prior, current)
    sourced_change = expected_change("marketing_sourced_pipeline", "relative", prior, current)
    efficiency_change = expected_change(
        "pipeline_per_marketing_dollar", "relative", prior, current
    )
    prior_bookings_per_win = float(prior["bookings"]) / float(prior["wins"])
    current_bookings_per_win = float(current["bookings"]) / float(current["wins"])
    bookings_per_win_change = (
        (current_bookings_per_win - prior_bookings_per_win)
        / prior_bookings_per_win
        * 100
    )

    errors.extend(
        require_markers(
            headline,
            "Headline",
            [
                f"{sourced_change:.1f}%",
                f"{abs(bookings_change):.1f}%",
                f"{abs(attainment_change):.1f} percentage points",
            ],
        )
    )

    regional_sorted = sorted(
        regional,
        key=lambda row: float(row["bookings_attainment"]),
    )
    lowest = regional_sorted[0]
    regional_markers = [
        f"{row['region']} had the lowest bookings attainment at "
        f"{float(row['bookings_attainment']) * 100:.1f}%"
        if row is lowest
        else f"{float(row['bookings_attainment']) * 100:.1f}%"
        for row in regional_sorted
    ]
    errors.extend(
        require_markers(
            changed,
            "What changed",
            [
                f"{sourced_change:.1f}%",
                f"{efficiency_change:.1f}%",
                f"{abs(bookings_change):.1f}%",
                *regional_markers,
            ],
        )
    )

    decision_lines = [
        line for line in decisions.splitlines() if re.match(r"^\d+\.\s", line)
    ]
    if len(decision_lines) != 3:
        errors.append(f"Three decisions: expected exactly 3 numbered decisions, found {len(decision_lines)}")
    for index, line in enumerate(decision_lines, start=1):
        for marker in ("Owner:", "Evidence:", "Next check:"):
            if marker not in line:
                errors.append(f"Decision {index}: missing {marker.rstrip(':').lower()}")

    errors.extend(
        require_markers(
            decisions,
            "Three decisions",
            [
                str(lowest["region"]),
                f"{float(lowest['bookings_attainment']) * 100:.1f}%",
                f"${float(current['pipeline_per_marketing_dollar']):.2f}",
                f"${float(prior['pipeline_per_marketing_dollar']):.2f}",
                str(current["wins"]),
                str(prior["wins"]),
                f"{abs(bookings_per_win_change):.1f}%",
                f"${current_bookings_per_win:,.0f}",
                f"${prior_bookings_per_win:,.0f}",
            ],
        )
    )
    return errors


def check(brief: str, raw_kpis: Any) -> list[str]:
    prior, current = normalize_rows(raw_kpis)
    _, regional = normalize_evidence(raw_kpis)
    errors: list[str] = []
    found: set[str] = set()

    for line in brief.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or cells[0] not in ROWS:
            continue
        label = cells[0]
        found.add(label)
        if len(cells) < 4:
            errors.append(f"{label}: expected four table cells")
            continue

        field, mode = ROWS[label]
        shown_current = parse_number(cells[1])
        shown_prior = parse_number(cells[2])
        shown_change = parse_number(cells[3])

        expected_current = displayed_value(field, current)
        expected_prior = displayed_value(field, prior)
        expected_delta = expected_change(field, mode, prior, current)
        is_rate = field in RATE_FIELDS

        if not close_enough(shown_current, expected_current, is_rate):
            errors.append(f"{label} current: brief shows {cells[1]!r}, source returned {current[field]}")
        if not close_enough(shown_prior, expected_prior, is_rate):
            errors.append(f"{label} prior: brief shows {cells[2]!r}, source returned {prior[field]}")
        if not close_enough(shown_change, expected_delta, True):
            errors.append(
                f"{label} change: brief shows {cells[3]!r}, expected {expected_delta:.4f}"
            )

    for label in ROWS:
        if label not in found:
            errors.append(f"Missing row from Key numbers table: {label}")
    errors.extend(check_narrative(brief, prior, current, regional))
    return errors


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python check_brief.py brief.md kpis.json")
    brief = Path(sys.argv[1]).read_text(encoding="utf-8")
    raw_kpis = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    errors = check(brief, raw_kpis)
    if errors:
        print("MISMATCH")
        for error in errors:
            print(f" - {error}")
        raise SystemExit(1)
    print("OK: Key numbers match executive_performance_metrics")


if __name__ == "__main__":
    main()
