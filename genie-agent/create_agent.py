"""Create the approved synthetic executive performance Genie Agent."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

TITLE = "Executive performance coworker (synthetic)"
DESCRIPTION = (
    "Synthetic weekly pipeline, finance, and marketing performance for executive operating reviews."
)


def cli(profile: str, *args: str) -> Any:
    result = subprocess.run(
        ["databricks", *args, "--profile", profile, "-o", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise SystemExit(result.stderr.strip())
    return json.loads(result.stdout)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    parser.add_argument("--warehouse-id", required=True)
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--template", type=Path, default=Path(__file__).with_name("agent-template.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    template = args.template.read_text(encoding="utf-8")
    serialized_space = template.replace("${catalog}", args.catalog).replace("${schema}", args.schema)
    json.loads(serialized_space)

    user = cli(args.profile, "current-user", "me")
    parent_path = f"/Workspace/Users/{user['userName']}/genie_spaces"
    subprocess.run(
        ["databricks", "workspace", "mkdirs", parent_path, "--profile", args.profile],
        check=True,
        capture_output=True,
        text=True,
    )

    response = cli(
        args.profile,
        "genie",
        "create-space",
        "--json",
        json.dumps(
            {
                "title": TITLE,
                "description": DESCRIPTION,
                "parent_path": parent_path,
                "warehouse_id": args.warehouse_id,
                "serialized_space": serialized_space,
            }
        ),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(response["space_id"], encoding="utf-8")
    print(f"Created Genie Agent: {TITLE}")


if __name__ == "__main__":
    main()
