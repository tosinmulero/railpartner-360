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
