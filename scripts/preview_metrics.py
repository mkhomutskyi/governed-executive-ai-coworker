"""Preview synthetic weekly KPIs without a Databricks connection."""

from __future__ import annotations

import json
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

REGIONS = {
    "North America": Decimal("1.00"),
    "EMEA": Decimal("0.78"),
    "Asia Pacific": Decimal("0.62"),
}
SEGMENTS = {
    "Enterprise": (Decimal("1.00"), Decimal("0.24")),
    "Mid-Market": (Decimal("0.66"), Decimal("0.29")),
}
CHANNELS = {
    "Paid Search": (Decimal("1.00"), Decimal("1.00"), Decimal("1.00")),
    "Events": (Decimal("1.35"), Decimal("0.72"), Decimal("1.24")),
    "Content": (Decimal("0.58"), Decimal("0.88"), Decimal("0.81")),
}


def rounded(value: Decimal, places: str = "0.01") -> Decimal:
    return value.quantize(Decimal(places), rounding=ROUND_HALF_UP)


def weekly_metrics(week_index: int) -> dict[str, float | int | str]:
    pipeline_created = Decimal(0)
    open_pipeline = Decimal(0)
    weighted_pipeline = Decimal(0)
    bookings = Decimal(0)
    opportunities_closed = 0
    wins = 0

    for region, region_factor in REGIONS.items():
        for segment, (segment_factor, win_rate) in SEGMENTS.items():
            pipeline_factor = Decimal("1.18") if week_index == 5 else Decimal(1)
            emea_factor = Decimal("0.91") if week_index == 5 and region == "EMEA" else Decimal(1)
            bookings_factor = Decimal(1)
            if week_index == 5:
                bookings_factor = {
                    "North America": Decimal("0.92"),
                    "EMEA": Decimal("0.76"),
                    "Asia Pacific": Decimal("0.98"),
                }[region]

            row_pipeline = rounded(
                (Decimal(310000) + week_index * Decimal(16000))
                * region_factor
                * segment_factor
                * pipeline_factor
            )
            row_open = rounded(
                (Decimal(1520000) + week_index * Decimal(42000))
                * region_factor
                * segment_factor
                * emea_factor
            )
            row_weighted = rounded(
                row_open * (Decimal("0.43") if segment == "Enterprise" else Decimal("0.36"))
            )
            row_bookings = rounded(
                (Decimal(216000) + week_index * Decimal(11500))
                * region_factor
                * segment_factor
                * bookings_factor
            )
            row_opportunities = int(
                rounded(
                    (Decimal(29) + week_index * Decimal("1.7"))
                    * region_factor
                    * (Decimal(2) - segment_factor),
                    "1",
                )
            )
            row_wins = int(rounded(Decimal(row_opportunities) * win_rate, "1"))

            pipeline_created += row_pipeline
            open_pipeline += row_open
            weighted_pipeline += row_weighted
            bookings += row_bookings
            opportunities_closed += row_opportunities
            wins += row_wins

    bookings_target = sum(
        rounded((Decimal(390000) + week_index * Decimal(12000)) * factor)
        for factor in REGIONS.values()
    )
    recognized_revenue = sum(
        rounded(
            (Decimal(348000) + week_index * Decimal(10500))
            * factor
            * (Decimal("0.96") if week_index == 5 else Decimal(1))
        )
        for factor in REGIONS.values()
    )
    revenue_target = sum(
        rounded((Decimal(360000) + week_index * Decimal(10000)) * factor)
        for factor in REGIONS.values()
    )

    marketing_spend = Decimal(0)
    qualified_leads = 0
    marketing_sourced_pipeline = Decimal(0)
    for region_factor in REGIONS.values():
        for spend_factor, lead_factor, pipeline_factor in CHANNELS.values():
            marketing_spend += rounded(
                (Decimal(22000) + week_index * Decimal(900))
                * region_factor
                * spend_factor
                * (Decimal("1.10") if week_index == 5 else Decimal(1))
            )
            qualified_leads += int(
                rounded(
                    (Decimal(118) + week_index * Decimal(4))
                    * region_factor
                    * lead_factor
                    * (Decimal("1.15") if week_index == 5 else Decimal(1)),
                    "1",
                )
            )
            marketing_sourced_pipeline += rounded(
                (Decimal(126000) + week_index * Decimal(6500))
                * region_factor
                * pipeline_factor
                * (Decimal("1.28") if week_index == 5 else Decimal(1))
            )

    week = date(2026, 8, 24) + timedelta(days=week_index * 7)
    return {
        "week": week.isoformat(),
        "pipeline_created": float(pipeline_created),
        "open_pipeline": float(open_pipeline),
        "weighted_pipeline": float(weighted_pipeline),
        "bookings": float(bookings),
        "bookings_target": float(bookings_target),
        "bookings_attainment": float(bookings / bookings_target),
        "recognized_revenue": float(recognized_revenue),
        "revenue_target": float(revenue_target),
        "revenue_attainment": float(recognized_revenue / revenue_target),
        "marketing_spend": float(marketing_spend),
        "marketing_sourced_pipeline": float(marketing_sourced_pipeline),
        "pipeline_per_marketing_dollar": float(marketing_sourced_pipeline / marketing_spend),
        "qualified_leads": qualified_leads,
        "cost_per_qualified_lead": float(marketing_spend / qualified_leads),
        "opportunities_closed": opportunities_closed,
        "wins": wins,
        "win_rate": wins / opportunities_closed,
    }


def main() -> None:
    print(json.dumps({"weekly_kpis": [weekly_metrics(4), weekly_metrics(5)]}, indent=2))


if __name__ == "__main__":
    main()
