with

searches as (

    select

        partner_id,

        count(*) as searches,

        count(*) filter (
            where converted_flag
        ) as converted_searches

    from {{ ref('stg_fact_searches') }}

    where partner_id is not null

    group by partner_id

),

bookings as (

    select

        partner_id,

        count(*) as bookings,

        sum(passenger_count) as passengers,

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
        ) as average_booking_value_gbp

    from {{ ref('stg_fact_bookings') }}

    where partner_id is not null

    group by partner_id

),

journeys as (

    select

        partner_id,

        count(*) as journeys,

        count(*) filter (
            where operational_disruption_flag
        ) as disrupted_journeys,

        count(*) filter (
            where journey_status = 'Operator Cancelled'
        ) as operator_cancellations

    from {{ ref('stg_fact_journeys') }}

    where partner_id is not null

    group by partner_id

),

refunds as (

    select

        partner_id,

        count(*) as refund_records,

        sum(
            refund_amount_gbp
        ) as refund_amount_gbp,

        sum(
            commercial_value_at_risk_gbp
        ) as commercial_value_at_risk_gbp

    from {{ ref('stg_fact_refunds') }}

    where partner_id is not null

    group by partner_id

)

select

    p.partner_id,
    p.partner_name,
    p.partner_type,
    p.partner_segment,
    p.service_tier,
    p.headquarters_region,

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
    ) as conversion_rate_pct,

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

    round(
        100.0
        * coalesce(
            j.disrupted_journeys,
            0
        )
        / nullif(
            j.journeys,
            0
        ),
        2
    ) as disruption_rate_pct,

    coalesce(
        j.operator_cancellations,
        0
    ) as operator_cancellations,

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

    round(
        coalesce(
            r.commercial_value_at_risk_gbp,
            0
        )::numeric,
        2
    ) as commercial_value_at_risk_gbp

from {{ ref('stg_dim_partner') }} p

left join searches s
    on p.partner_id = s.partner_id

left join bookings b
    on p.partner_id = b.partner_id

left join journeys j
    on p.partner_id = j.partner_id

left join refunds r
    on p.partner_id = r.partner_id
