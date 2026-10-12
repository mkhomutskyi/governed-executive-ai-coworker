/* Inspect the row counts of the synthetic sources and shared-grain view. */
SELECT
  (SELECT COUNT(*) FROM ${catalog}.${schema}.sales_pipeline_weekly) AS sales_rows,
  (SELECT COUNT(*) FROM ${catalog}.${schema}.finance_weekly) AS finance_rows,
  (SELECT COUNT(*) FROM ${catalog}.${schema}.marketing_weekly) AS marketing_rows,
  (SELECT COUNT(*) FROM ${catalog}.${schema}.executive_weekly_signals) AS signal_rows;
