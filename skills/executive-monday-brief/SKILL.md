---
name: executive-monday-brief
description: Creates a one-page Monday executive brief from synthetic pipeline, finance, and marketing metrics, with exact week-over-week KPIs and three evidence-backed decisions. Use when asked for the executive weekly brief, cross-functional operating review, pipeline and finance summary, or marketing efficiency update.
---

# Executive Monday brief

Produce a decision brief for one calendar week of synthetic B2B software data. Governed metrics provide every number. A Genie Agent may explain patterns. Its generated prose can still misstate numbers or derived comparisons, so check those against query results before presenting the brief.

## Inputs

- `week_start`: a Monday in `YYYY-MM-DD` format.
- Optional focus: company, one region, or one metric.
- If no week is provided, ask for one. For the packaged sample, suggest `2026-09-28`.

## Required sources

List the data tools available in the session before calling them. Do not guess tool names.

1. The `executive_performance_metrics` metric view for every KPI.
2. The "Executive performance coworker (synthetic)" Genie Agent for at most two explanatory questions.
3. The template at `references/brief-template.md`.
4. In Genie Code, the validator at `scripts/check_brief.py`.

If the metric view is unavailable, stop and identify the missing source. Never reconstruct these KPIs from raw tables.

## Steps

1. Confirm that `week_start` is a Monday. If not, suggest the Monday of that week and ask before continuing.
2. Query the requested week and prior week from the metric view. Return:
   - Pipeline Created
   - Bookings
   - Bookings Target
   - Bookings Attainment
   - Recognized Revenue
   - Revenue Attainment
   - Marketing Spend
   - Marketing-Sourced Pipeline
   - Pipeline per Marketing Dollar
   - Qualified Leads
   - Cost per Qualified Lead
   - Opportunities Closed
   - Wins
   - Bookings per Win
   - Win Rate
3. Query the requested week by Region for Bookings Attainment, Pipeline Created, and Pipeline per Marketing Dollar.
4. Identify the largest favorable change, the largest unfavorable change, and the region requiring attention.
5. Ask the Genie Agent at most two focused questions about those patterns. Use its explanation only when it cites the governed source and provides its SQL.
6. Write the brief with `references/brief-template.md`. Include exactly three proposed decisions, each with an owner, evidence, and a next check.
7. Save the two weekly KPI rows and requested-week regional rows as one JSON evidence object. Run `scripts/check_brief.py <brief.md> <kpis.json>`. Fix every mismatch before presenting the brief. The validator compares the 12-row KPI table, looks for selected headline/regional/decision value markers, and checks the three-decision format with owner, evidence, and next-check fields. It does not understand every narrative statement. Review direction, derived comparisons, and proposed actions independently.
8. Output a draft for review. Do not send, post, publish, or modify another system.

## Query pattern

Use the fully qualified metric-view name discovered in the session.

```sql
SELECT
  `Week`,
  MEASURE(`Pipeline Created`) AS pipeline_created,
  MEASURE(`Bookings`) AS bookings,
  MEASURE(`Bookings Target`) AS bookings_target,
  MEASURE(`Bookings Attainment`) AS bookings_attainment,
  MEASURE(`Recognized Revenue`) AS recognized_revenue,
  MEASURE(`Revenue Attainment`) AS revenue_attainment,
  MEASURE(`Marketing Spend`) AS marketing_spend,
  MEASURE(`Marketing-Sourced Pipeline`) AS marketing_sourced_pipeline,
  MEASURE(`Pipeline per Marketing Dollar`) AS pipeline_per_marketing_dollar,
  MEASURE(`Qualified Leads`) AS qualified_leads,
  MEASURE(`Cost per Qualified Lead`) AS cost_per_qualified_lead,
  MEASURE(`Opportunities Closed`) AS opportunities_closed,
  MEASURE(`Wins`) AS wins,
  MEASURE(`Bookings per Win`) AS bookings_per_win,
  MEASURE(`Win Rate`) AS win_rate
FROM <catalog>.<schema>.executive_performance_metrics
WHERE `Week` IN (DATE '<week_start>', DATE '<prior_week_start>')
GROUP BY ALL
ORDER BY `Week`
```

## Rules

- A number used anywhere in the brief must match the metric-view result.
- Format currency to the nearest dollar, counts as whole numbers, and rates to one decimal percentage point.
- Describe Pipeline per Marketing Dollar as a ratio such as `$4.80 pipeline per $1 spent`, not as ROI.
- Before explaining a Bookings change, compare Win Rate and Bookings per Win. Do not label the issue conversion friction when Win Rate is flat; investigate value per win, deal size, or discounting when Bookings per Win declines.
- Write comparisons as "X this week vs Y prior week". Do not use arrows.
- Say that the dataset is synthetic.
- Distinguish observed evidence from proposed action.
- Do not claim causation. Use "coincided with", "is consistent with", or "needs investigation".
- If a query or tool fails, disclose the gap instead of estimating.
- Keep the brief under 350 words.
