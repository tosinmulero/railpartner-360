select

    booking_id,
    search_id,
    customer_id,
    partner_id,
    route_id,
    ticket_id,

    booking_timestamp,
    travel_date::date as travel_date,

    booking_lead_days,
    sales_channel,
    business_traveller_flag,
    passenger_count,

    booked_fare_gbp,
    gross_booking_value_gbp,
    discount_rate,
    discount_amount_gbp,
    net_ticket_value_gbp,
    commission_rate,
    commission_revenue_gbp,
    service_fee_gbp,
    platform_revenue_gbp,

    payment_method,
    promotion_used_flag,
    booking_status

from {{ source('raw', 'fact_bookings') }}
