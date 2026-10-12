# Optional executive Genie Agent

The Agent answers follow-up questions from the governed `executive_performance_metrics` metric view. It is separate from the brief skill's direct metric queries.

`agent-template.json` includes parameterized data sources, reviewed metadata, rate-format instructions, and four benchmark questions: bookings versus target, pipeline and marketing efficiency, regional attainment, and Win Rate.

Replace the catalog and schema through `create_agent.py`, and use an existing SQL warehouse. The helper creates a new Agent and writes its identifier only to the local output path you choose. See [the setup guide](../docs/SETUP.md).

Keep rates fractional in SQL and display them as percentages. Treat marketing attribution as association; do not infer causation. People review proposed decisions and any generated calculations.
