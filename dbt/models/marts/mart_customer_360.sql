with

searches as (

    select

        customer_id,

        count(*) as searches,

        count(*) filter (
            where converted_flag
        ) as converted_searches,

        min(
            search_date
        ) as first_search_date,

        max(
            search_date
        ) as latest_search_date

    from {{ ref('stg_fact_searches') }}

    group by customer_id

),

bookings as (

    select

        customer_id,

        count(*) as bookings,

        sum(
            passenger_count
        ) as passengers,

        sum(
            gross_booking_value_gbp
        ) as gross_booking_value_gbp,

        sum(
            net_ticket_value_gbp
        ) as net_ticket_value_gbp,

        sum(
            platform_revenue_gbp
        ) as platform_revenue_gbp,

        avg(
            gross_booking_value_gbp
        ) as average_booking_value_gbp,

        min(
            booking_timestamp
        ) as first_booking_timestamp,

        max(
            booking_timestamp
        ) as latest_booking_timestamp

    from {{ ref('stg_fact_bookings') }}

    group by customer_id

),

journeys as (

    select

        customer_id,

        count(*) as journeys,

        count(*) filter (
            where operational_disruption_flag
        ) as disrupted_journeys,

        count(*) filter (
            where journey_status = 'Operator Cancelled'
        ) as operator_cancelled_journeys

    from {{ ref('stg_fact_journeys') }}

    group by customer_id

),

refunds as (

    select

        customer_id,

        count(*) as refund_records,

        sum(
            refund_amount_gbp
        ) as refund_amount_gbp

    from {{ ref('stg_fact_refunds') }}

    group by customer_id

)

select

    c.customer_id,
    c.signup_date,
    c.customer_segment,
    c.home_region,
    c.loyalty_tier,
    c.preferred_device,
    c.acquisition_channel,
    c.age_band,
    c.business_traveller_flag,
    c.marketing_opt_in,

    coalesce(
        s.searches,
        0
    ) as searches,

    coalesce(
        b.bookings,
        0
    ) as bookings,

    round(
        100.0
        * coalesce(
            b.bookings,
            0
        )
        / nullif(
            s.searches,
            0
        ),
        2
    ) as customer_conversion_rate_pct,

    coalesce(
        b.passengers,
        0
    ) as passengers,

    round(
        coalesce(
            b.gross_booking_value_gbp,
            0
        )::numeric,
        2
    ) as gross_booking_value_gbp,

    round(
        coalesce(
            b.net_ticket_value_gbp,
            0
        )::numeric,
        2
    ) as net_ticket_value_gbp,

    round(
        coalesce(
            b.platform_revenue_gbp,
            0
        )::numeric,
        2
    ) as platform_revenue_gbp,

    round(
        coalesce(
            b.average_booking_value_gbp,
            0
        )::numeric,
        2
    ) as average_booking_value_gbp,

    coalesce(
        j.journeys,
        0
    ) as journeys,

    coalesce(
        j.disrupted_journeys,
        0
    ) as disrupted_journeys,

    coalesce(
        j.operator_cancelled_journeys,
        0
    ) as operator_cancelled_journeys,

    coalesce(
        r.refund_records,
        0
    ) as refund_records,

    round(
        coalesce(
            r.refund_amount_gbp,
            0
        )::numeric,
        2
    ) as refund_amount_gbp,

    s.first_search_date,
    s.latest_search_date,

    b.first_booking_timestamp,
    b.latest_booking_timestamp

from {{ ref('stg_dim_customer') }} c

left join searches s
    on c.customer_id = s.customer_id

left join bookings b
    on c.customer_id = b.customer_id

left join journeys j
    on c.customer_id = j.customer_id

left join refunds r
    on c.customer_id = r.customer_id
