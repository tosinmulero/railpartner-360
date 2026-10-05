select

    journey_id,
    booking_id,
    customer_id,
    partner_id,
    route_id,
    operator_id,
    ticket_id,

    travel_date::date as travel_date,

    scheduled_departure,
    scheduled_arrival,
    actual_departure,
    actual_arrival,

    planned_duration_minutes,
    distance_km,
    route_type,

    journey_status,

    departure_delay_minutes,
    arrival_delay_minutes,
    delay_band,

    within_3_minutes_flag,
    within_15_minutes_flag,
    severe_delay_flag,
    operational_disruption_flag,

    disruption_reason,

    compensation_eligible_flag,
    business_traveller_flag,
    sales_channel

from {{ source('raw', 'fact_journeys') }}
