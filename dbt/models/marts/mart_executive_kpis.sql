with

search_metrics as (

    select

        count(*) as total_searches,

        count(*) filter (
            where availability_flag
        ) as available_searches,

        count(*) filter (
            where converted_flag
        ) as converted_searches

    from {{ ref('stg_fact_searches') }}

),

booking_metrics as (

    select

        count(*) as total_bookings,

        sum(passenger_count) as total_passengers,

        sum(gross_booking_value_gbp) as gross_booking_value_gbp,

        sum(net_ticket_value_gbp) as net_ticket_value_gbp,

        sum(platform_revenue_gbp) as platform_revenue_gbp,

        avg(gross_booking_value_gbp) as average_booking_value_gbp,

        count(*) filter (
            where partner_id is not null
        ) as b2b_bookings

    from {{ ref('stg_fact_bookings') }}

),

journey_metrics as (

    select

        count(*) as total_journeys,

        count(*) filter (
            where journey_status = 'Completed'
        ) as completed_journeys,

        count(*) filter (
            where journey_status = 'Operator Cancelled'
        ) as operator_cancelled_journeys,

        count(*) filter (
            where operational_disruption_flag
        ) as disrupted_journeys,

        count(*) filter (
            where within_3_minutes_flag
        ) as within_3_minutes_journeys,

        count(*) filter (
            where journey_status = 'Completed'
        ) as punctuality_denominator

    from {{ ref('stg_fact_journeys') }}

),

refund_metrics as (

    select

        count(*) as refund_records,

        sum(refund_amount_gbp) as total_refund_amount_gbp,

        sum(
            commercial_value_at_risk_gbp
        ) as commercial_value_at_risk_gbp

    from {{ ref('stg_fact_refunds') }}

)

select

    s.total_searches,
    s.available_searches,
    s.converted_searches,

    b.total_bookings,
    b.total_passengers,

    round(
        100.0
        * b.total_bookings
        / nullif(
            s.total_searches,
            0
        ),
        2
    ) as conversion_rate_pct,

    round(
        b.gross_booking_value_gbp::numeric,
        2
    ) as gross_booking_value_gbp,

    round(
        b.net_ticket_value_gbp::numeric,
        2
    ) as net_ticket_value_gbp,

    round(
        b.platform_revenue_gbp::numeric,
        2
    ) as platform_revenue_gbp,

    round(
        b.average_booking_value_gbp::numeric,
        2
    ) as average_booking_value_gbp,

    round(
        100.0
        * b.b2b_bookings
        / nullif(
            b.total_bookings,
            0
        ),
        2
    ) as b2b_booking_share_pct,

    j.total_journeys,
    j.completed_journeys,
    j.operator_cancelled_journeys,
    j.disrupted_journeys,

    round(
        100.0
        * j.operator_cancelled_journeys
        / nullif(
            j.total_journeys,
            0
        ),
        2
    ) as operator_cancellation_rate_pct,

    round(
        100.0
        * j.disrupted_journeys
        / nullif(
            j.total_journeys,
            0
        ),
        2
    ) as disruption_rate_pct,

    round(
        100.0
        * j.within_3_minutes_journeys
        / nullif(
            j.punctuality_denominator,
            0
        ),
        2
    ) as within_3_minutes_pct,

    r.refund_records,

    round(
        r.total_refund_amount_gbp::numeric,
        2
    ) as total_refund_amount_gbp,

    round(
        r.commercial_value_at_risk_gbp::numeric,
        2
    ) as commercial_value_at_risk_gbp

from search_metrics s

cross join booking_metrics b

cross join journey_metrics j

cross join refund_metrics r
