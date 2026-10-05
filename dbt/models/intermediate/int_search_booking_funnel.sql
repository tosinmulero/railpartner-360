select

    s.search_id,
    s.customer_id,
    s.partner_id,
    s.route_id,

    s.search_timestamp,
    s.search_date,
    s.travel_date,

    s.booking_lead_days,
    s.sales_channel,
    s.customer_segment,
    s.business_traveller_flag,
    s.route_type,

    s.distance_km,
    s.result_count,
    s.lowest_fare_gbp,

    s.availability_flag,
    s.converted_flag,

    b.booking_id,
    b.booking_timestamp,

    b.passenger_count,
    b.gross_booking_value_gbp,
    b.net_ticket_value_gbp,
    b.platform_revenue_gbp,

    b.promotion_used_flag,
    b.booking_status

from {{ ref('stg_fact_searches') }} s

left join {{ ref('stg_fact_bookings') }} b
    on s.search_id = b.search_id
