select

    refund_id,
    booking_id,
    journey_id,
    customer_id,
    partner_id,

    refund_type,
    refund_reason,
    refund_status,

    refund_request_timestamp,
    refund_processed_timestamp,

    eligible_value_gbp,
    refund_rate,
    refund_amount_gbp,
    commercial_value_at_risk_gbp,

    processing_days,

    business_traveller_flag,
    sales_channel

from {{ source('raw', 'fact_refunds') }}
