select

    ticket_id,
    ticket_name,
    journey_type,
    fare_category,
    refundable_flag,
    changeable_flag

from {{ source('raw', 'dim_ticket') }}
