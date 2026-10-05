select

    date_trunc(
        'month',
        search_date
    )::date as month,

    sales_channel,

    business_traveller_flag,

    customer_segment,

    count(*) as searches,

    count(*) filter (
        where availability_flag
    ) as searches_with_availability,

    count(*) filter (
        where converted_flag
    ) as bookings,

    round(
        100.0
        * count(*) filter (
            where converted_flag
        )
        / nullif(
            count(*),
            0
        ),
        2
    ) as conversion_rate_pct,

    round(
        avg(
            lowest_fare_gbp
        )::numeric,
        2
    ) as average_lowest_fare_gbp,

    round(
        avg(
            booking_lead_days
        )::numeric,
        2
    ) as average_booking_lead_days

from {{ ref('stg_fact_searches') }}

group by

    date_trunc(
        'month',
        search_date
    ),

    sales_channel,

    business_traveller_flag,

    customer_segment
