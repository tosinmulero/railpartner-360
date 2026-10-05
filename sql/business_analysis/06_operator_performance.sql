select
    operator_id,
    operator_name,
    service_type,

    sum(journeys) as journeys,
    sum(completed_journeys) as completed_journeys,
    sum(operator_cancellations) as operator_cancellations,
    sum(disrupted_journeys) as disrupted_journeys,
    sum(severe_delay_journeys) as severe_delay_journeys,

    round(
        100.0
        * sum(operator_cancellations)
        / nullif(
            sum(journeys),
            0
        ),
        2
    ) as cancellation_rate_pct,

    round(
        100.0
        * sum(disrupted_journeys)
        / nullif(
            sum(journeys),
            0
        ),
        2
    ) as disruption_rate_pct,

    round(
        avg(
            within_3_minutes_pct
        ),
        2
    ) as average_within_3_minutes_pct,

    round(
        avg(
            average_arrival_delay_minutes
        ),
        2
    ) as average_arrival_delay_minutes

from marts.mart_operational_performance

group by
    operator_id,
    operator_name,
    service_type

order by
    disruption_rate_pct desc,
    cancellation_rate_pct desc;
