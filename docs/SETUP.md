# Set up the executive brief demo

Use a sandbox catalog and schema that you are authorized to modify. The data-loading SQL creates or replaces the demo tables and views; review it before running. Use an existing SQL warehouse.

## 1. Prepare your tools

Install Python 3.11 or later and the [Databricks CLI](https://docs.databricks.com/aws/en/dev-tools/cli/install). Authenticate with a local profile. Keep credentials and live outputs outside version control; `local/` is ignored by Git.

The SQL requires a Unity Catalog workspace with metric-view support. For non-commercial learning, you can use [Databricks Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition). Its [limitations](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations) include quotas and restricted features. Do not use customer data in this public demo.

The commands below use Bash variables. In PowerShell, use `$ProfileName`, `$WarehouseId`, `$CatalogName`, and `$SchemaName` with your own values.

```bash
PROFILE="<your-profile>"
WAREHOUSE_ID="<existing-warehouse-id>"
CATALOG="<sandbox-catalog>"
SCHEMA="<sandbox-schema>"
```

## 2. Load the synthetic data and define the metrics

Run these files in order, either in the SQL editor after replacing `${catalog}` and `${schema}`, or with the included runner:

```bash
python scripts/run_sql.py sql/01_synthetic_data.sql --profile "$PROFILE" --warehouse-id "$WAREHOUSE_ID" --catalog "$CATALOG" --schema "$SCHEMA"
python scripts/run_sql.py sql/02_executive_weekly_signals.sql --profile "$PROFILE" --warehouse-id "$WAREHOUSE_ID" --catalog "$CATALOG" --schema "$SCHEMA"
python scripts/run_sql.py metric-views/executive_performance_metrics.sql --profile "$PROFILE" --warehouse-id "$WAREHOUSE_ID" --catalog "$CATALOG" --schema "$SCHEMA"
```

Sales begins at week × region × segment; marketing at week × region × channel; finance at week × region. The base view aggregates first, then joins at week × region. This avoids repeating finance targets across segment/channel combinations.

## 3. Inspect and query

```bash
python scripts/run_sql.py sql/04_data_checks.sql --profile "$PROFILE" --warehouse-id "$WAREHOUSE_ID" --catalog "$CATALOG" --schema "$SCHEMA"
python scripts/run_sql.py sql/06_workflow_checks.sql --profile "$PROFILE" --warehouse-id "$WAREHOUSE_ID" --catalog "$CATALOG" --schema "$SCHEMA"
python scripts/run_sql.py sql/03_metric_queries.sql --profile "$PROFILE" --warehouse-id "$WAREHOUSE_ID" --catalog "$CATALOG" --schema "$SCHEMA"
python scripts/run_sql.py sql/05_brief_queries.sql --profile "$PROFILE" --warehouse-id "$WAREHOUSE_ID" --catalog "$CATALOG" --schema "$SCHEMA"
```

The final file returns weekly and regional inputs for the brief. Save your results locally as an object with `weekly` and `regional` lists, using [examples/kpis.json](../examples/kpis.json) as the shape. SQL rates stay fractional; format them as percentages in the brief. Compute changes from unrounded values.

## 4. Draft and check the brief

Use [the brief skill](../skills/executive-monday-brief/SKILL.md) and [its template](../skills/executive-monday-brief/references/brief-template.md). The packaged example is [examples/monday-brief.md](../examples/monday-brief.md).

```bash
python skills/executive-monday-brief/scripts/check_brief.py examples/monday-brief.md examples/kpis.json
```

For your own brief, replace those paths with your local brief and query results. The checker compares the 12 KPI rows, selected narrative values, and the owner/evidence/next-check format of three proposed decisions. Review the rest of the narrative and all calculated comparisons yourself.

## 5. Optional: create the Genie Agent

The [parameterized Agent template](../genie-agent/agent-template.json) provides four benchmark questions. Creating the Agent writes a new workspace object; it does not create compute, publish the Agent, or grant access.

```bash
python genie-agent/create_agent.py --profile "$PROFILE" --warehouse-id "$WAREHOUSE_ID" --catalog "$CATALOG" --schema "$SCHEMA" --output local/agent-id.txt
```

Use [Databricks' Agent setup guidance](https://docs.databricks.com/aws/en/genie-agents/set-up) to review permissions and [testing guidance](https://docs.databricks.com/aws/en/genie-agents/monitor) to expand the workload. A 4/4 result on the bundled questions is a bounded check, not a production-readiness certificate.
