with

searches as (

    select

        route_id,

        count(*) as searches,

        count(*) filter (
            where converted_flag
        ) as converted_searches

    from {{ ref('stg_fact_searches') }}

    group by route_id

),

bookings as (

    select

        route_id,

        count(*) as bookings,

        sum(
            gross_booking_value_gbp
        ) as gross_booking_value_gbp,

        sum(
            platform_revenue_gbp
        ) as platform_revenue_gbp

    from {{ ref('stg_fact_bookings') }}

    group by route_id

),

journeys as (

    select

        route_id,

        count(*) as journeys,

        count(*) filter (
            where operational_disruption_flag
        ) as disrupted_journeys,

        count(*) filter (
            where journey_status = 'Operator Cancelled'
        ) as operator_cancellations,

        avg(
            arrival_delay_minutes
        ) filter (
            where journey_status = 'Completed'
        ) as average_arrival_delay_minutes,

        count(*) filter (
            where within_3_minutes_flag
        ) as within_3_minutes_journeys,

        count(*) filter (
            where journey_status = 'Completed'
        ) as completed_journeys

    from {{ ref('stg_fact_journeys') }}

    group by route_id

)

select

    r.route_id,

    origin.station_name as origin_station,
    destination.station_name as destination_station,

    r.distance_km,
    r.route_type,
    r.planned_duration_minutes,

    o.operator_name,

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

    round(
        coalesce(
            b.gross_booking_value_gbp,
            0
        )::numeric,
        2
    ) as gross_booking_value_gbp,

    round(
        coalesce(
            b.platform_revenue_gbp,
            0
        )::numeric,
        2
    ) as platform_revenue_gbp,

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

    round(
        coalesce(
            j.average_arrival_delay_minutes,
            0
        )::numeric,
        2
    ) as average_arrival_delay_minutes,

    round(
        100.0
        * coalesce(
            j.within_3_minutes_journeys,
            0
        )
        / nullif(
            j.completed_journeys,
            0
        ),
        2
    ) as within_3_minutes_pct

from {{ ref('stg_dim_route') }} r

left join {{ ref('stg_dim_station') }} origin
    on r.origin_station_id = origin.station_id

left join {{ ref('stg_dim_station') }} destination
    on r.destination_station_id = destination.station_id

left join {{ ref('stg_dim_operator') }} o
    on r.primary_operator_id = o.operator_id

left join searches s
    on r.route_id = s.route_id

left join bookings b
    on r.route_id = b.route_id

left join journeys j
    on r.route_id = j.route_id
