from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "skills" / "executive-monday-brief" / "scripts" / "check_brief.py"
SPEC = importlib.util.spec_from_file_location("check_brief", CHECKER_PATH)
assert SPEC and SPEC.loader
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


KPIS = [
    {
        "week": "2026-09-21",
        "pipeline_created": 100.0,
        "bookings": 100.0,
        "bookings_target": 100.0,
        "bookings_attainment": 0.75,
        "recognized_revenue": 100.0,
        "revenue_attainment": 0.8,
        "marketing_spend": 100.0,
        "marketing_sourced_pipeline": 100.0,
        "pipeline_per_marketing_dollar": 4.0,
        "qualified_leads": 100,
        "cost_per_qualified_lead": 100.0,
        "win_rate": 0.25,
    },
    {
        "week": "2026-09-28",
        "pipeline_created": 120.0,
        "bookings": 120.0,
        "bookings_target": 120.0,
        "bookings_attainment": 0.8,
        "recognized_revenue": 120.0,
        "revenue_attainment": 0.85,
        "marketing_spend": 120.0,
        "marketing_sourced_pipeline": 120.0,
        "pipeline_per_marketing_dollar": 5.0,
        "qualified_leads": 110,
        "cost_per_qualified_lead": 90.0,
        "win_rate": 0.30,
    },
]

GOOD_BRIEF = """
| Metric | This week | Prior week | Change |
|---|---:|---:|---:|
| Pipeline created | $120 | $100 | +20.0% |
| Bookings | $120 | $100 | +20.0% |
| Bookings target | $120 | $100 | +20.0% |
| Bookings attainment | 80.0% | 75.0% | +5.0 pp |
| Recognized revenue | $120 | $100 | +20.0% |
| Revenue attainment | 85.0% | 80.0% | +5.0 pp |
| Marketing spend | $120 | $100 | +20.0% |
| Marketing-sourced pipeline | $120 | $100 | +20.0% |
| Pipeline per marketing dollar | $5.00 per $1 | $4.00 per $1 | +25.0% |
| Qualified leads | 110 | 100 | +10.0% |
| Cost per qualified lead | $90 | $100 | -10.0% |
| Win rate | 30.0% | 25.0% | +5.0 pp |
"""


class BriefCheckerTest(unittest.TestCase):
    def test_accepts_matching_metric_view_values(self) -> None:
        self.assertEqual(CHECKER.check(GOOD_BRIEF, KPIS), [])

    def test_rejects_planted_booking_error(self) -> None:
        bad_brief = GOOD_BRIEF.replace("| Bookings | $120 |", "| Bookings | $150 |")
        errors = CHECKER.check(bad_brief, KPIS)
        self.assertTrue(any("Bookings current" in error for error in errors))

    def test_rejects_missing_row(self) -> None:
        brief_without_win_rate = "\n".join(
            line for line in GOOD_BRIEF.splitlines() if not line.startswith("| Win rate |")
        )
        errors = CHECKER.check(brief_without_win_rate, KPIS)
        self.assertIn("Missing row from Key numbers table: Win rate", errors)

    def test_rejects_nonconsecutive_weeks(self) -> None:
        bad_kpis = [dict(KPIS[0]), dict(KPIS[1], week="2026-10-05")]
        with self.assertRaisesRegex(ValueError, "consecutive"):
            CHECKER.check(GOOD_BRIEF, bad_kpis)

    def test_accepts_complete_published_brief(self) -> None:
        brief = (ROOT / "examples" / "monday-brief.md").read_text()
        evidence = json.loads(
            (ROOT / "examples" / "kpis.json").read_text()
        )
        self.assertEqual(CHECKER.check(brief, evidence), [])

    def test_rejects_corrupted_headline(self) -> None:
        brief = (ROOT / "examples" / "monday-brief.md").read_text()
        evidence = json.loads(
            (ROOT / "examples" / "kpis.json").read_text()
        )
        bad_brief = brief.replace("rose 33.5%", "rose 999.9%", 1)
        errors = CHECKER.check(bad_brief, evidence)
        self.assertTrue(any("Headline" in error for error in errors))

    def test_rejects_corrupted_regional_evidence(self) -> None:
        brief = (ROOT / "examples" / "monday-brief.md").read_text()
        evidence = json.loads(
            (ROOT / "examples" / "kpis.json").read_text()
        )
        bad_brief = brief.replace("EMEA had the lowest bookings attainment at 76.7%", "EMEA had the lowest bookings attainment at 99.9%")
        errors = CHECKER.check(bad_brief, evidence)
        self.assertTrue(any("What changed" in error for error in errors))

    def test_rejects_missing_decision_owner(self) -> None:
        brief = (ROOT / "examples" / "monday-brief.md").read_text()
        evidence = json.loads(
            (ROOT / "examples" / "kpis.json").read_text()
        )
        bad_brief = brief.replace("Owner: Regional sales lead.", "Regional sales lead.")
        errors = CHECKER.check(bad_brief, evidence)
        self.assertIn("Decision 1: missing owner", errors)

    def test_rejects_corrupted_value_per_win_evidence(self) -> None:
        brief = (ROOT / "examples" / "monday-brief.md").read_text()
        evidence = json.loads(
            (ROOT / "examples" / "kpis.json").read_text()
        )
        bad_brief = brief.replace("$16,889", "$99,999")
        errors = CHECKER.check(bad_brief, evidence)
        self.assertTrue(any("Three decisions" in error for error in errors))

    def test_rejects_extra_decision(self) -> None:
        brief = (ROOT / "examples" / "monday-brief.md").read_text()
        evidence = json.loads(
            (ROOT / "examples" / "kpis.json").read_text()
        )
        bad_brief = brief.replace(
            "\n## Caveat and sources",
            "\n4. **Unapproved extra action** - Owner: CFO. Evidence: none. Next check: Friday.\n\n## Caveat and sources",
        )
        errors = CHECKER.check(bad_brief, evidence)
        self.assertTrue(any("expected exactly 3" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
