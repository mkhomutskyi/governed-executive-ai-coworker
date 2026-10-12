/* Read-only structural and decision-evidence checks. */
/* Replace ${catalog} and ${schema} before execution. */

WITH
sales_duplicate_keys AS (
  SELECT week_start, region, customer_segment
  FROM ${catalog}.${schema}.sales_pipeline_weekly
  GROUP BY ALL
  HAVING COUNT(*) <> 1
),
finance_duplicate_keys AS (
  SELECT week_start, region
  FROM ${catalog}.${schema}.finance_weekly
  GROUP BY ALL
  HAVING COUNT(*) <> 1
),
marketing_duplicate_keys AS (
  SELECT week_start, region, channel
  FROM ${catalog}.${schema}.marketing_weekly
  GROUP BY ALL
  HAVING COUNT(*) <> 1
),
signal_duplicate_keys AS (
  SELECT week_start, region
  FROM ${catalog}.${schema}.executive_weekly_signals
  GROUP BY ALL
  HAVING COUNT(*) <> 1
),
expected_keys AS (
  SELECT week_start, region FROM ${catalog}.${schema}.sales_pipeline_weekly
  UNION
  SELECT week_start, region FROM ${catalog}.${schema}.finance_weekly
  UNION
  SELECT week_start, region FROM ${catalog}.${schema}.marketing_weekly
),
sales_keys AS (
  SELECT DISTINCT week_start, region
  FROM ${catalog}.${schema}.sales_pipeline_weekly
),
finance_keys AS (
  SELECT DISTINCT week_start, region
  FROM ${catalog}.${schema}.finance_weekly
),
marketing_keys AS (
  SELECT DISTINCT week_start, region
  FROM ${catalog}.${schema}.marketing_weekly
)
SELECT
  (SELECT COUNT(*) FROM ${catalog}.${schema}.sales_pipeline_weekly) AS sales_rows,
  (SELECT COUNT(*) FROM ${catalog}.${schema}.finance_weekly) AS finance_rows,
  (SELECT COUNT(*) FROM ${catalog}.${schema}.marketing_weekly) AS marketing_rows,
  (SELECT COUNT(*) FROM ${catalog}.${schema}.executive_weekly_signals) AS signal_rows,
  (SELECT COUNT(*) FROM sales_duplicate_keys) AS sales_duplicate_keys,
  (SELECT COUNT(*) FROM finance_duplicate_keys) AS finance_duplicate_keys,
  (SELECT COUNT(*) FROM marketing_duplicate_keys) AS marketing_duplicate_keys,
  (SELECT COUNT(*) FROM signal_duplicate_keys) AS signal_duplicate_keys,
  (
    SELECT COUNT(*)
    FROM expected_keys e
    LEFT ANTI JOIN sales_keys s USING (week_start, region)
  ) AS missing_sales_keys,
  (
    SELECT COUNT(*)
    FROM expected_keys e
    LEFT ANTI JOIN finance_keys f USING (week_start, region)
  ) AS missing_finance_keys,
  (
    SELECT COUNT(*)
    FROM expected_keys e
    LEFT ANTI JOIN marketing_keys m USING (week_start, region)
  ) AS missing_marketing_keys;

SELECT
  `Week` AS week,
  MEASURE(`Bookings`) AS bookings,
  MEASURE(`Opportunities Closed`) AS opportunities_closed,
  MEASURE(`Wins`) AS wins,
  MEASURE(`Win Rate`) AS win_rate,
  MEASURE(`Bookings`) / NULLIF(MEASURE(`Wins`), 0) AS bookings_per_win
FROM ${catalog}.${schema}.executive_performance_metrics
WHERE `Week` IN (DATE '2026-09-21', DATE '2026-09-28')
GROUP BY ALL
ORDER BY week;
