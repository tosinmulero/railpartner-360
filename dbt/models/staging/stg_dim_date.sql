select

    date_id,
    date::date as calendar_date,
    year,
    quarter,
    month_number,
    month_name,
    year_month,
    week_number,
    day_of_month,
    day_name,
    day_of_week,
    weekend_flag,
    season

from {{ source('raw', 'dim_date') }}
