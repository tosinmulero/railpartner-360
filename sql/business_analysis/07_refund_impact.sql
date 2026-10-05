select
    refund_type,
    refund_reason,
    sales_channel,
    business_traveller_flag,

    sum(refund_records) as refund_records,

    round(
        sum(
            eligible_value_gbp
        ),
        2
    ) as eligible_value_gbp,

    round(
        sum(
            refund_amount_gbp
        ),
        2
    ) as refund_amount_gbp,

    round(
        sum(
            commercial_value_at_risk_gbp
        ),
        2
    ) as commercial_value_at_risk_gbp,

    round(
        avg(
            average_processing_days
        ),
        2
    ) as average_processing_days

from marts.mart_refund_impact

group by
    refund_type,
    refund_reason,
    sales_channel,
    business_traveller_flag

order by
    commercial_value_at_risk_gbp desc;
