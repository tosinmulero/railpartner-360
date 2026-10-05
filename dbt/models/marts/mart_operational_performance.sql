select

    date_trunc(
        'month',
        j.travel_date
    )::date as month,

    j.operator_id,

    o.operator_name,

    o.service_type,

    count(*) as journeys,

    count(*) filter (
        where j.journey_status = 'Completed'
    ) as completed_journeys,

    count(*) filter (
        where j.journey_status = 'Operator Cancelled'
    ) as operator_cancellations,

    count(*) filter (
        where j.operational_disruption_flag
    ) as disrupted_journeys,

    count(*) filter (
        where j.severe_delay_flag
    ) as severe_delay_journeys,

    round(
        100.0
        * count(*) filter (
            where j.within_3_minutes_flag
        )
        / nullif(
            count(*) filter (
                where j.journey_status = 'Completed'
            ),
            0
        ),
        2
    ) as within_3_minutes_pct,

    round(
        100.0
        * count(*) filter (
            where j.journey_status = 'Operator Cancelled'
        )
        / nullif(
            count(*),
            0
        ),
        2
    ) as operator_cancellation_rate_pct,

    round(
        100.0
        * count(*) filter (
            where j.operational_disruption_flag
        )
        / nullif(
            count(*),
            0
        ),
        2
    ) as disruption_rate_pct,

    round(
        avg(
            j.arrival_delay_minutes
        ) filter (
            where j.journey_status = 'Completed'
        )::numeric,
        2
    ) as average_arrival_delay_minutes

from {{ ref('stg_fact_journeys') }} j

left join {{ ref('stg_dim_operator') }} o
    on j.operator_id = o.operator_id

group by

    date_trunc(
        'month',
        j.travel_date
    ),

    j.operator_id,

    o.operator_name,

    o.service_type
