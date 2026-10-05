select

    customer_id,
    signup_date::date as signup_date,
    customer_segment,
    home_region,
    loyalty_tier,
    preferred_device,
    acquisition_channel,
    age_band,
    business_traveller_flag,
    marketing_opt_in

from {{ source('raw', 'dim_customer') }}
