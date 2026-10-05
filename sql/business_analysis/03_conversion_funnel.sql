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
