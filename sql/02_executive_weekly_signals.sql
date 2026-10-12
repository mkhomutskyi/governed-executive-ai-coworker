/* Fan-out-safe base view at one row per week and region. */
/* Replace ${catalog} and ${schema} before execution. */

CREATE OR REPLACE VIEW ${catalog}.${schema}.executive_weekly_signals
COMMENT 'Synthetic cross-functional weekly signals at one row per Monday and region. Sales and marketing facts are aggregated before they are joined to finance.'
AS
WITH sales AS (
  SELECT
    week_start,
    region,
    SUM(pipeline_created) AS pipeline_created,
    SUM(open_pipeline) AS open_pipeline,
    SUM(weighted_pipeline) AS weighted_pipeline,
    SUM(bookings) AS bookings,
    SUM(opportunities_closed) AS opportunities_closed,
    SUM(wins) AS wins
  FROM ${catalog}.${schema}.sales_pipeline_weekly
  GROUP BY week_start, region
),
marketing AS (
  SELECT
    week_start,
    region,
    SUM(marketing_spend) AS marketing_spend,
    SUM(qualified_leads) AS qualified_leads,
    SUM(sourced_pipeline) AS marketing_sourced_pipeline
  FROM ${catalog}.${schema}.marketing_weekly
  GROUP BY week_start, region
)
SELECT
  s.week_start,
  s.region,
  s.pipeline_created,
  s.open_pipeline,
  s.weighted_pipeline,
  s.bookings,
  f.bookings_target,
  f.recognized_revenue,
  f.revenue_target,
  m.marketing_spend,
  m.qualified_leads,
  m.marketing_sourced_pipeline,
  s.opportunities_closed,
  s.wins
FROM sales s
INNER JOIN ${catalog}.${schema}.finance_weekly f
  ON s.week_start = f.week_start
  AND s.region = f.region
INNER JOIN marketing m
  ON s.week_start = m.week_start
  AND s.region = m.region;
