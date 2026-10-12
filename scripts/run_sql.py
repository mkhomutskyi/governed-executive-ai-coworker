"""Execute a local SQL file through the Databricks Statement Execution API."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any

IDENTIFIER = re.compile(r"^[A-Za-z0-9_]+$")
DATE_LITERAL = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SPACE_ID = re.compile(r"^[a-f0-9]{32}$")


def cli(profile: str, *args: str) -> dict[str, Any]:
    result = subprocess.run(
        ["databricks", *args, "--profile", profile, "-o", "json"],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def statements(path: Path, replacements: dict[str, str]) -> list[str]:
    sql = path.read_text(encoding="utf-8")
    for placeholder, value in replacements.items():
        sql = sql.replace(placeholder, value)
    unresolved = sorted(set(re.findall(r"\$\{[^}]+\}", sql)))
    if unresolved:
        raise SystemExit(f"Unresolved SQL placeholders: {', '.join(unresolved)}")
    return [statement.strip() for statement in re.split(r";\s*(?:\n|$)", sql) if statement.strip()]


def execute(profile: str, warehouse_id: str, statement: str) -> dict[str, Any]:
    response = cli(
        profile,
        "api",
        "post",
        "/api/2.0/sql/statements/",
        "--json",
        json.dumps(
            {
                "warehouse_id": warehouse_id,
                "statement": statement,
                "wait_timeout": "50s",
            }
        ),
    )
    while response["status"]["state"] in {"PENDING", "RUNNING"}:
        time.sleep(1)
        response = cli(
            profile,
            "api",
            "get",
            f"/api/2.0/sql/statements/{response['statement_id']}",
        )
    return response


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--warehouse-id", required=True)
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--space-id")
    args = parser.parse_args()

    for value, label in ((args.catalog, "catalog"), (args.schema, "schema")):
        if not IDENTIFIER.fullmatch(value):
            raise SystemExit(f"Unsafe {label} identifier: {value!r}")

    replacements = {"${catalog}": args.catalog, "${schema}": args.schema}
    for value, label in ((args.start_date, "start date"), (args.end_date, "end date")):
        if value:
            if not DATE_LITERAL.fullmatch(value):
                raise SystemExit(f"Unsafe {label}: {value!r}")
            replacements[f"${{{label.replace(' ', '_')}}}"] = value
    if args.space_id:
        if not SPACE_ID.fullmatch(args.space_id):
            raise SystemExit("Unsafe Genie Agent ID")
        replacements["${space_id}"] = args.space_id

    for index, statement in enumerate(statements(args.path, replacements), start=1):
        response = execute(args.profile, args.warehouse_id, statement)
        state = response["status"]["state"]
        label = " ".join(statement.split()[:6])
        print(f"{index}: {state} - {label}")
        if state != "SUCCEEDED":
            error = response["status"].get("error", {})
            print(json.dumps(error, indent=2))
            raise SystemExit(1)
        rows = response.get("result", {}).get("data_array", [])
        if rows:
            columns = [column["name"] for column in response["manifest"]["schema"]["columns"]]
            for row in rows:
                print(json.dumps(dict(zip(columns, row, strict=True)), sort_keys=True))


if __name__ == "__main__":
    main()
