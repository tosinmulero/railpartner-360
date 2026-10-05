select

    station_id,
    station_code,
    station_name,
    region,
    station_category,
    annual_entries_estimate,
    interchange_flag,
    synthetic_flag

from {{ source('raw', 'dim_station') }}
