/* Weekly company performance for the article's example week and prior week. */
SELECT
  `Week`,
  MEASURE(`Pipeline Created`) AS pipeline_created,
  MEASURE(`Bookings`) AS bookings,
  MEASURE(`Bookings Target`) AS bookings_target,
  MEASURE(`Bookings Attainment`) AS bookings_attainment,
  MEASURE(`Marketing Spend`) AS marketing_spend,
  MEASURE(`Marketing-Sourced Pipeline`) AS marketing_sourced_pipeline,
  MEASURE(`Pipeline per Marketing Dollar`) AS pipeline_per_marketing_dollar
FROM ${catalog}.${schema}.executive_performance_metrics
WHERE `Week` IN (DATE '2026-09-21', DATE '2026-09-28')
GROUP BY ALL
ORDER BY `Week`;

/* Regional performance for the example week. */
SELECT
  `Region`,
  MEASURE(`Pipeline Created`) AS pipeline_created,
  MEASURE(`Bookings Attainment`) AS bookings_attainment,
  MEASURE(`Pipeline per Marketing Dollar`) AS pipeline_per_marketing_dollar
FROM ${catalog}.${schema}.executive_performance_metrics
WHERE `Week` = DATE '2026-09-28'
GROUP BY ALL
ORDER BY bookings_attainment;

/* Marketing efficiency trend. */
SELECT
  `Week`,
  MEASURE(`Marketing Spend`) AS marketing_spend,
  MEASURE(`Marketing-Sourced Pipeline`) AS marketing_sourced_pipeline,
  MEASURE(`Pipeline per Marketing Dollar`) AS pipeline_per_marketing_dollar,
  MEASURE(`Cost per Qualified Lead`) AS cost_per_qualified_lead
FROM ${catalog}.${schema}.executive_performance_metrics
GROUP BY ALL
ORDER BY `Week`;

/* Bookings value per win by region for the example week. */
SELECT
  `Region`,
  MEASURE(`Bookings`) AS bookings,
  MEASURE(`Wins`) AS wins,
  MEASURE(`Bookings per Win`) AS bookings_per_win
FROM ${catalog}.${schema}.executive_performance_metrics
WHERE `Week` = DATE '2026-09-28'
GROUP BY ALL
ORDER BY bookings_per_win
LIMIT 3;

/* Sales conversion trend. */
SELECT
  `Week`,
  MEASURE(`Opportunities Closed`) AS opportunities_closed,
  MEASURE(`Wins`) AS wins,
  MEASURE(`Win Rate`) AS win_rate
FROM ${catalog}.${schema}.executive_performance_metrics
GROUP BY ALL
ORDER BY `Week`;
