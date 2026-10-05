from pathlib import Path

ROOT = Path.cwd()

SQL_DIR = ROOT / "sql" / "business_analysis"
REPORT_DIR = ROOT / "reports" / "executive"

SQL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

queries = {

"01_executive_kpis.sql": r"""
select
    total_searches,
    total_bookings,
    total_passengers,
    conversion_rate_pct,
    gross_booking_value_gbp,
    net_ticket_value_gbp,
    platform_revenue_gbp,
    average_booking_value_gbp,
    b2b_booking_share_pct,
    total_journeys,
    completed_journeys,
    operator_cancelled_journeys,
    disruption_rate_pct,
    operator_cancellation_rate_pct,
    within_3_minutes_pct,
    refund_records,
    total_refund_amount_gbp,
    commercial_value_at_risk_gbp
from marts.mart_executive_kpis;
""",

"02_partner_opportunity.sql": r"""
select
    partner_id,
    partner_name,
    partner_type,
    partner_segment,
    service_tier,
    searches,
    bookings,
    conversion_rate_pct,
    gross_booking_value_gbp,
    platform_revenue_gbp,
    disruption_rate_pct,
    operator_cancellations,
    refund_records,
    refund_amount_gbp,
    commercial_value_at_risk_gbp,

    round(
        platform_revenue_gbp
        / nullif(bookings, 0),
        2
    ) as revenue_per_booking_gbp,

    dense_rank() over (
        order by platform_revenue_gbp desc
    ) as revenue_rank,

    dense_rank() over (
        order by conversion_rate_pct desc
    ) as conversion_rank,

    dense_rank() over (
        order by commercial_value_at_risk_gbp desc
    ) as risk_rank

from marts.mart_partner_performance

where bookings > 0

order by platform_revenue_gbp desc;
""",

"03_conversion_funnel.sql": r"""
select
    sales_channel,
    customer_segment,
    business_traveller_flag,

    sum(searches) as searches,

    sum(
        searches_with_availability
    ) as searches_with_availability,

    sum(bookings) as bookings,

    round(
        100.0
        * sum(bookings)
        / nullif(
            sum(searches),
            0
        ),
        2
    ) as conversion_rate_pct,

    round(
        avg(
            average_lowest_fare_gbp
        ),
        2
    ) as average_lowest_fare_gbp,

    round(
        avg(
            average_booking_lead_days
        ),
        2
    ) as average_booking_lead_days

from marts.mart_conversion_funnel

group by
    sales_channel,
    customer_segment,
    business_traveller_flag

order by
    conversion_rate_pct desc,
    searches desc;
""",

"04_customer_segments.sql": r"""
select
    customer_segment,
    loyalty_tier,
    business_traveller_flag,

    count(*) as customers,

    sum(searches) as searches,
    sum(bookings) as bookings,

    round(
        100.0
        * sum(bookings)
        / nullif(
            sum(searches),
            0
        ),
        2
    ) as conversion_rate_pct,

    round(
        sum(
            gross_booking_value_gbp
        ),
        2
    ) as gross_booking_value_gbp,

    round(
        sum(
            platform_revenue_gbp
        ),
        2
    ) as platform_revenue_gbp,

    round(
        avg(
            average_booking_value_gbp
        ),
        2
    ) as average_booking_value_gbp,

    sum(
        disrupted_journeys
    ) as disrupted_journeys,

    sum(
        refund_records
    ) as refund_records,

    round(
        sum(
            refund_amount_gbp
        ),
        2
    ) as refund_amount_gbp

from marts.mart_customer_360

group by
    customer_segment,
    loyalty_tier,
    business_traveller_flag

order by
    platform_revenue_gbp desc;
""",

"05_route_opportunity.sql": r"""
select
    route_id,
    origin_station,
    destination_station,
    operator_name,
    route_type,
    distance_km,

    searches,
    bookings,
    conversion_rate_pct,

    gross_booking_value_gbp,
    platform_revenue_gbp,

    journeys,
    disrupted_journeys,
    disruption_rate_pct,

    operator_cancellations,
    average_arrival_delay_minutes,
    within_3_minutes_pct,

    round(
        platform_revenue_gbp
        / nullif(bookings, 0),
        2
    ) as revenue_per_booking_gbp,

    case
        when conversion_rate_pct >= 35
             and disruption_rate_pct >= 10
            then 'Protect High Demand'

        when conversion_rate_pct < 30
             and searches >= 5000
            then 'Conversion Opportunity'

        when platform_revenue_gbp >= 10000
             and disruption_rate_pct < 8
            then 'High-Value Stable'

        else 'Monitor'
    end as commercial_priority

from marts.mart_route_performance

where searches > 0

order by
    platform_revenue_gbp desc;
""",

"06_operator_performance.sql": r"""
select
    operator_id,
    operator_name,
    service_type,

    sum(journeys) as journeys,
    sum(completed_journeys) as completed_journeys,
    sum(operator_cancellations) as operator_cancellations,
    sum(disrupted_journeys) as disrupted_journeys,
    sum(severe_delay_journeys) as severe_delay_journeys,

    round(
        100.0
        * sum(operator_cancellations)
        / nullif(
            sum(journeys),
            0
        ),
        2
    ) as cancellation_rate_pct,

    round(
        100.0
        * sum(disrupted_journeys)
        / nullif(
            sum(journeys),
            0
        ),
        2
    ) as disruption_rate_pct,

    round(
        avg(
            within_3_minutes_pct
        ),
        2
    ) as average_within_3_minutes_pct,

    round(
        avg(
            average_arrival_delay_minutes
        ),
        2
    ) as average_arrival_delay_minutes

from marts.mart_operational_performance

group by
    operator_id,
    operator_name,
    service_type

order by
    disruption_rate_pct desc,
    cancellation_rate_pct desc;
""",

"07_refund_impact.sql": r"""
select
    refund_type,
    refund_reason,
    sales_channel,
    business_traveller_flag,

    sum(refund_records) as refund_records,

    round(
        sum(
            eligible_value_gbp
        ),
        2
    ) as eligible_value_gbp,

    round(
        sum(
            refund_amount_gbp
        ),
        2
    ) as refund_amount_gbp,

    round(
        sum(
            commercial_value_at_risk_gbp
        ),
        2
    ) as commercial_value_at_risk_gbp,

    round(
        avg(
            average_processing_days
        ),
        2
    ) as average_processing_days

from marts.mart_refund_impact

group by
    refund_type,
    refund_reason,
    sales_channel,
    business_traveller_flag

order by
    commercial_value_at_risk_gbp desc;
"""
}

for filename, sql in queries.items():

    path = SQL_DIR / filename

    path.write_text(
        sql.strip() + "\n",
        encoding="utf-8"
    )

    print(f"[CREATED] {path}")

print()
print("Stage 7 SQL files created.")
