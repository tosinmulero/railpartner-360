select

    search_id,
    customer_id,
    partner_id,
    route_id,

    search_timestamp,
    search_date::date as search_date,
    travel_date::date as travel_date,

    booking_lead_days,
    sales_channel,
    customer_segment,
    business_traveller_flag,
    route_type,
    distance_km,
    result_count,
    lowest_fare_gbp,
    availability_flag,
    converted_flag

from {{ source('raw', 'fact_searches') }}
