select

    b.booking_id,
    b.search_id,
    b.customer_id,
    b.partner_id,
    b.route_id,
    b.ticket_id,

    b.booking_timestamp,
    b.travel_date,
    b.booking_lead_days,

    b.sales_channel,
    b.business_traveller_flag,

    b.passenger_count,
    b.gross_booking_value_gbp,
    b.discount_amount_gbp,
    b.net_ticket_value_gbp,
    b.commission_revenue_gbp,
    b.service_fee_gbp,
    b.platform_revenue_gbp,

    b.payment_method,
    b.promotion_used_flag,
    b.booking_status,

    c.customer_segment,
    c.home_region,
    c.loyalty_tier,
    c.preferred_device,
    c.acquisition_channel as customer_acquisition_channel,

    p.partner_name,
    p.partner_type,
    p.partner_segment,
    p.service_tier,

    r.origin_station_id,
    r.destination_station_id,
    r.primary_operator_id,
    r.distance_km,
    r.route_type,
    r.planned_duration_minutes,

    o.operator_name,
    o.service_type as operator_service_type,

    t.ticket_name,
    t.journey_type,
    t.fare_category,

    j.journey_id,
    j.journey_status,
    j.departure_delay_minutes,
    j.arrival_delay_minutes,
    j.delay_band,
    j.within_3_minutes_flag,
    j.within_15_minutes_flag,
    j.severe_delay_flag,
    j.operational_disruption_flag,
    j.disruption_reason,
    j.compensation_eligible_flag

from {{ ref('stg_fact_bookings') }} b

left join {{ ref('stg_fact_journeys') }} j
    on b.booking_id = j.booking_id

left join {{ ref('stg_dim_customer') }} c
    on b.customer_id = c.customer_id

left join {{ ref('stg_dim_partner') }} p
    on b.partner_id = p.partner_id

left join {{ ref('stg_dim_route') }} r
    on b.route_id = r.route_id

left join {{ ref('stg_dim_operator') }} o
    on j.operator_id = o.operator_id

left join {{ ref('stg_dim_ticket') }} t
    on b.ticket_id = t.ticket_id
