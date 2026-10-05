select

    operator_id,
    operator_name,
    service_type,
    synthetic_flag

from {{ source('raw', 'dim_operator') }}
