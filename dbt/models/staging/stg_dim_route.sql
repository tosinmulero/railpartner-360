select

    route_id,
    origin_station_id,
    destination_station_id,
    primary_operator_id,
    distance_km,
    route_type,
    planned_duration_minutes,
    active_flag

from {{ source('raw', 'dim_route') }}
