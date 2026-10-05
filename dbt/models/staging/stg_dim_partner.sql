select

    partner_id,
    partner_name,
    partner_type,
    partner_segment,
    service_tier,
    headquarters_region,
    acquisition_channel,
    contract_start_date::date as contract_start_date,
    commission_rate,
    active_flag

from {{ source('raw', 'dim_partner') }}
