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
