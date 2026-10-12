/* Deterministic synthetic data for the executive coworker demo. */
/* Replace ${catalog} and ${schema} before execution. */

CREATE OR REPLACE TABLE ${catalog}.${schema}.sales_pipeline_weekly (
  week_start DATE COMMENT 'Monday that starts the calendar week',
  region STRING COMMENT 'Synthetic sales region',
  customer_segment STRING COMMENT 'Synthetic customer segment',
  pipeline_created DECIMAL(18, 2) COMMENT 'New qualified pipeline created during the week in USD',
  open_pipeline DECIMAL(18, 2) COMMENT 'Open pipeline at the end of the week in USD',
  weighted_pipeline DECIMAL(18, 2) COMMENT 'Open pipeline multiplied by stage probability in USD',
  bookings DECIMAL(18, 2) COMMENT 'Closed-won contract value during the week in USD',
  opportunities_closed BIGINT COMMENT 'Opportunities resolved as won or lost during the week',
  wins BIGINT COMMENT 'Closed-won opportunities during the week'
)
USING DELTA
COMMENT 'Synthetic weekly sales and pipeline facts for a B2B software company.';

INSERT OVERWRITE ${catalog}.${schema}.sales_pipeline_weekly
WITH weeks AS (
  SELECT explode(sequence(DATE '2026-08-24', DATE '2026-10-05', INTERVAL 7 DAYS)) AS week_start
),
indexed_weeks AS (
  SELECT
    week_start,
    CAST(DATEDIFF(week_start, DATE '2026-08-24') / 7 AS INT) AS week_index
  FROM weeks
),
regions(region, region_factor) AS (
  VALUES
    ('North America', 1.00),
    ('EMEA', 0.78),
    ('Asia Pacific', 0.62)
),
segments(customer_segment, segment_factor, win_rate) AS (
  VALUES
    ('Enterprise', 1.00, 0.24),
    ('Mid-Market', 0.66, 0.29)
),
generated AS (
  SELECT
    w.week_start,
    w.week_index,
    r.region,
    r.region_factor,
    s.customer_segment,
    s.segment_factor,
    s.win_rate,
    ROUND(
      (310000 + w.week_index * 16000) * r.region_factor * s.segment_factor
      * CASE WHEN w.week_index = 5 THEN 1.18 ELSE 1.00 END,
      2
    ) AS pipeline_created,
    ROUND(
      (1520000 + w.week_index * 42000) * r.region_factor * s.segment_factor
      * CASE
          WHEN w.week_index = 5 AND r.region = 'EMEA' THEN 0.91
          ELSE 1.00
        END,
      2
    ) AS open_pipeline,
    ROUND(
      (216000 + w.week_index * 11500) * r.region_factor * s.segment_factor
      * CASE
          WHEN w.week_index = 5 AND r.region = 'North America' THEN 0.92
          WHEN w.week_index = 5 AND r.region = 'EMEA' THEN 0.76
          WHEN w.week_index = 5 AND r.region = 'Asia Pacific' THEN 0.98
          ELSE 1.00
        END,
      2
    ) AS bookings,
    CAST(
      ROUND((29 + w.week_index * 1.7) * r.region_factor * (2.0 - s.segment_factor))
      AS BIGINT
    ) AS opportunities_closed
  FROM indexed_weeks w
  CROSS JOIN regions r
  CROSS JOIN segments s
)
SELECT
  week_start,
  region,
  customer_segment,
  CAST(pipeline_created AS DECIMAL(18, 2)),
  CAST(open_pipeline AS DECIMAL(18, 2)),
  CAST(ROUND(open_pipeline * CASE customer_segment WHEN 'Enterprise' THEN 0.43 ELSE 0.36 END, 2) AS DECIMAL(18, 2)),
  CAST(bookings AS DECIMAL(18, 2)),
  opportunities_closed,
  CAST(ROUND(opportunities_closed * win_rate) AS BIGINT)
FROM generated;

CREATE OR REPLACE TABLE ${catalog}.${schema}.finance_weekly (
  week_start DATE COMMENT 'Monday that starts the calendar week',
  region STRING COMMENT 'Synthetic finance region',
  bookings_target DECIMAL(18, 2) COMMENT 'Weekly bookings target in USD',
  recognized_revenue DECIMAL(18, 2) COMMENT 'Revenue recognized during the week in USD',
  revenue_target DECIMAL(18, 2) COMMENT 'Weekly recognized revenue target in USD'
)
USING DELTA
COMMENT 'Synthetic weekly finance actuals and targets for a B2B software company.';

INSERT OVERWRITE ${catalog}.${schema}.finance_weekly
WITH weeks AS (
  SELECT explode(sequence(DATE '2026-08-24', DATE '2026-10-05', INTERVAL 7 DAYS)) AS week_start
),
indexed_weeks AS (
  SELECT
    week_start,
    CAST(DATEDIFF(week_start, DATE '2026-08-24') / 7 AS INT) AS week_index
  FROM weeks
),
regions(region, region_factor) AS (
  VALUES
    ('North America', 1.00),
    ('EMEA', 0.78),
    ('Asia Pacific', 0.62)
)
SELECT
  w.week_start,
  r.region,
  CAST(ROUND((390000 + w.week_index * 12000) * r.region_factor, 2) AS DECIMAL(18, 2)),
  CAST(
    ROUND(
      (348000 + w.week_index * 10500) * r.region_factor
      * CASE WHEN w.week_index = 5 THEN 0.96 ELSE 1.00 END,
      2
    )
    AS DECIMAL(18, 2)
  ),
  CAST(ROUND((360000 + w.week_index * 10000) * r.region_factor, 2) AS DECIMAL(18, 2))
FROM indexed_weeks w
CROSS JOIN regions r;

CREATE OR REPLACE TABLE ${catalog}.${schema}.marketing_weekly (
  week_start DATE COMMENT 'Monday that starts the calendar week',
  region STRING COMMENT 'Synthetic marketing region',
  channel STRING COMMENT 'Synthetic demand-generation channel',
  marketing_spend DECIMAL(18, 2) COMMENT 'Marketing spend during the week in USD',
  qualified_leads BIGINT COMMENT 'Marketing-qualified leads created during the week',
  sourced_pipeline DECIMAL(18, 2) COMMENT 'Pipeline attributed to the channel during the week in USD'
)
USING DELTA
COMMENT 'Synthetic weekly marketing spend, qualified leads, and sourced pipeline.';

INSERT OVERWRITE ${catalog}.${schema}.marketing_weekly
WITH weeks AS (
  SELECT explode(sequence(DATE '2026-08-24', DATE '2026-10-05', INTERVAL 7 DAYS)) AS week_start
),
indexed_weeks AS (
  SELECT
    week_start,
    CAST(DATEDIFF(week_start, DATE '2026-08-24') / 7 AS INT) AS week_index
  FROM weeks
),
regions(region, region_factor) AS (
  VALUES
    ('North America', 1.00),
    ('EMEA', 0.78),
    ('Asia Pacific', 0.62)
),
channels(channel, spend_factor, lead_factor, pipeline_factor) AS (
  VALUES
    ('Paid Search', 1.00, 1.00, 1.00),
    ('Events', 1.35, 0.72, 1.24),
    ('Content', 0.58, 0.88, 0.81)
)
SELECT
  w.week_start,
  r.region,
  c.channel,
  CAST(
    ROUND(
      (22000 + w.week_index * 900) * r.region_factor * c.spend_factor
      * CASE WHEN w.week_index = 5 THEN 1.10 ELSE 1.00 END,
      2
    )
    AS DECIMAL(18, 2)
  ),
  CAST(
    ROUND(
      (118 + w.week_index * 4.0) * r.region_factor * c.lead_factor
      * CASE WHEN w.week_index = 5 THEN 1.15 ELSE 1.00 END
    )
    AS BIGINT
  ),
  CAST(
    ROUND(
      (126000 + w.week_index * 6500) * r.region_factor * c.pipeline_factor
      * CASE WHEN w.week_index = 5 THEN 1.28 ELSE 1.00 END,
      2
    )
    AS DECIMAL(18, 2)
  )
FROM indexed_weeks w
CROSS JOIN regions r
CROSS JOIN channels c;
