/* Governed evidence for the 2026-09-28 synthetic executive brief. */

SELECT
  `Week` AS week,
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
  MEASURE(`Wins`) AS wins,
  MEASURE(`Win Rate`) AS win_rate
FROM ${catalog}.${schema}.executive_performance_metrics
WHERE `Week` IN (DATE '2026-09-21', DATE '2026-09-28')
GROUP BY ALL
ORDER BY `Week`;

SELECT
  `Region` AS region,
  MEASURE(`Bookings Attainment`) AS bookings_attainment,
  MEASURE(`Pipeline Created`) AS pipeline_created,
  MEASURE(`Pipeline per Marketing Dollar`) AS pipeline_per_marketing_dollar
FROM ${catalog}.${schema}.executive_performance_metrics
WHERE `Week` = DATE '2026-09-28'
GROUP BY ALL
ORDER BY bookings_attainment;
