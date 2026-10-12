import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREVIEW_PATH = ROOT / "scripts" / "preview_metrics.py"
SPEC = importlib.util.spec_from_file_location("preview_metrics", PREVIEW_PATH)
assert SPEC and SPEC.loader
PREVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREVIEW)


def test_weekly_preview_matches_published_decision_signals() -> None:
    prior = PREVIEW.weekly_metrics(4)
    current = PREVIEW.weekly_metrics(5)

    def relative_change(field: str) -> float:
        return round(
            (float(current[field]) - float(prior[field])) / float(prior[field]) * 100,
            1,
        )

    assert prior["week"] == "2026-09-21"
    assert current["week"] == "2026-09-28"
    assert relative_change("pipeline_created") == 23.0
    assert relative_change("bookings") == -7.8
    assert relative_change("marketing_sourced_pipeline") == 33.5
    assert relative_change("pipeline_per_marketing_dollar") == 17.2
    assert round(
        (float(current["bookings_attainment"]) - float(prior["bookings_attainment"])) * 100,
        1,
    ) == -10.2
