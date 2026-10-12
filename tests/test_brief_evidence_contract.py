"""Check that the documented SQL projection supplies full brief validation."""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_sql_07_projection_supports_full_published_brief_validation():
    sql = (ROOT / "sql/05_brief_queries.sql").read_text(encoding="utf-8")
    weekly_query, regional_query, _ = sql.split(";")
    weekly_fields = re.findall(r"\bAS\s+(\w+)", weekly_query, flags=re.IGNORECASE)
    regional_fields = re.findall(r"\bAS\s+(\w+)", regional_query, flags=re.IGNORECASE)
    saved = json.loads((ROOT / "examples/kpis.json").read_text(encoding="utf-8"))
    projected = {
        "weekly": [{key: row[key] for key in weekly_fields} for row in saved["weekly"]],
        "regional": [{key: row[key] for key in regional_fields} for row in saved["regional"]],
    }
    spec = importlib.util.spec_from_file_location("contract_checker", ROOT / "skills/executive-monday-brief/scripts/check_brief.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    brief = (ROOT / "examples/monday-brief.md").read_text(encoding="utf-8")
    assert checker.check(brief, projected) == []
    assert [row["wins"] for row in projected["weekly"]] == [55, 57]
