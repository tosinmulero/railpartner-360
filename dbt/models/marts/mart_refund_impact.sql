select

    date_trunc(
        'month',
        refund_request_timestamp
    )::date as month,

    refund_type,
    refund_reason,
    refund_status,
    sales_channel,
    business_traveller_flag,

    count(*) as refund_records,

    round(
        sum(
            eligible_value_gbp
        )::numeric,
        2
    ) as eligible_value_gbp,

    round(
        sum(
            refund_amount_gbp
        )::numeric,
        2
    ) as refund_amount_gbp,

    round(
        sum(
            commercial_value_at_risk_gbp
        )::numeric,
        2
    ) as commercial_value_at_risk_gbp,

    round(
        avg(
            processing_days
        )::numeric,
        2
    ) as average_processing_days

from {{ ref('stg_fact_refunds') }}

group by

    date_trunc(
        'month',
        refund_request_timestamp
    ),

    refund_type,
    refund_reason,
    refund_status,
    sales_channel,
    business_traveller_flag
