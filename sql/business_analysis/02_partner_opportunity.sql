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
