CREATE OR REPLACE VIEW ${catalog}.${schema}.executive_performance_metrics
WITH METRICS
LANGUAGE YAML
AS $$
  version: 1.1
  source: ${catalog}.${schema}.executive_weekly_signals
  comment: "Governed weekly pipeline, finance, and marketing metrics for a synthetic B2B software executive operating review."
  dimensions:
    - name: Week
      expr: week_start
      comment: "Monday that starts the calendar week."
      display_name: "Week"
      synonyms:
        - "week starting"
        - "reporting week"
    - name: Region
      expr: region
      comment: "Synthetic go-to-market region."
      display_name: "Region"
      synonyms:
        - "sales region"
        - "market"
  measures:
    - name: Pipeline Created
      expr: SUM(pipeline_created)
      comment: "New qualified pipeline created during the selected period, in USD."
      display_name: "Pipeline Created"
      synonyms:
        - "new pipeline"
        - "pipeline generated"
    - name: Bookings
      expr: SUM(bookings)
      comment: "Closed-won contract value during the selected period, in USD."
      display_name: "Bookings"
      synonyms:
        - "closed won value"
        - "sales bookings"
    - name: Bookings Target
      expr: SUM(bookings_target)
      comment: "Finance-approved bookings target for the selected period, in USD."
      display_name: "Bookings Target"
      synonyms:
        - "bookings plan"
        - "sales target"
    - name: Bookings Attainment
      expr: "MEASURE(`Bookings`) / NULLIF(MEASURE(`Bookings Target`), 0)"
      comment: "Bookings divided by the finance-approved bookings target, expressed as a fraction."
      display_name: "Bookings Attainment"
      synonyms:
        - "attainment"
        - "bookings versus plan"
    - name: Recognized Revenue
      expr: SUM(recognized_revenue)
      comment: "Revenue recognized during the selected period, in USD."
      display_name: "Recognized Revenue"
      synonyms:
        - "revenue"
        - "actual revenue"
    - name: Revenue Target
      expr: SUM(revenue_target)
      comment: "Finance-approved recognized revenue target for the selected period, in USD."
      display_name: "Revenue Target"
      synonyms:
        - "revenue plan"
    - name: Revenue Attainment
      expr: "MEASURE(`Recognized Revenue`) / NULLIF(MEASURE(`Revenue Target`), 0)"
      comment: "Recognized revenue divided by the finance-approved revenue target, expressed as a fraction."
      display_name: "Revenue Attainment"
      synonyms:
        - "revenue versus plan"
    - name: Marketing Spend
      expr: SUM(marketing_spend)
      comment: "Marketing spend during the selected period, in USD."
      display_name: "Marketing Spend"
      synonyms:
        - "demand generation spend"
    - name: Marketing-Sourced Pipeline
      expr: SUM(marketing_sourced_pipeline)
      comment: "Pipeline attributed to marketing activity during the selected period, in USD."
      display_name: "Marketing-Sourced Pipeline"
      synonyms:
        - "marketing pipeline"
        - "sourced pipeline"
    - name: Pipeline per Marketing Dollar
      expr: "MEASURE(`Marketing-Sourced Pipeline`) / NULLIF(MEASURE(`Marketing Spend`), 0)"
      comment: "Marketing-sourced pipeline generated per USD of marketing spend."
      display_name: "Pipeline per Marketing Dollar"
      synonyms:
        - "pipeline efficiency"
        - "pipeline return on spend"
    - name: Qualified Leads
      expr: SUM(qualified_leads)
      comment: "Marketing-qualified leads created during the selected period."
      display_name: "Qualified Leads"
      synonyms:
        - "MQLs"
        - "marketing-qualified leads"
    - name: Cost per Qualified Lead
      expr: "MEASURE(`Marketing Spend`) / NULLIF(MEASURE(`Qualified Leads`), 0)"
      comment: "Marketing spend divided by qualified leads, in USD per lead."
      display_name: "Cost per Qualified Lead"
      synonyms:
        - "cost per MQL"
        - "lead acquisition cost"
    - name: Opportunities Closed
      expr: SUM(opportunities_closed)
      comment: "Opportunities resolved as won or lost during the selected period."
      display_name: "Opportunities Closed"
      synonyms:
        - "resolved opportunities"
    - name: Wins
      expr: SUM(wins)
      comment: "Closed-won opportunities during the selected period."
      display_name: "Wins"
      synonyms:
        - "won opportunities"
    - name: Bookings per Win
      expr: "MEASURE(`Bookings`) / NULLIF(MEASURE(`Wins`), 0)"
      comment: "Closed-won contract value divided by closed-won opportunities, in USD per win."
      display_name: "Bookings per Win"
      synonyms:
        - "average deal value"
        - "value per win"
    - name: Win Rate
      expr: "MEASURE(`Wins`) / NULLIF(MEASURE(`Opportunities Closed`), 0)"
      comment: "Closed-won opportunities divided by all opportunities resolved during the selected period, expressed as a fraction."
      display_name: "Win Rate"
      synonyms:
        - "sales win rate"
        - "close rate"
$$;
