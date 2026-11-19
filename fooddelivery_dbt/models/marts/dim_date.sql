with spine as (

    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2025-01-01' as date)",
        end_date="cast('2027-01-01' as date)"
    ) }}

)

select
    cast(date_day as date)                      as date_day,
    year(date_day)                              as year,
    quarter(date_day)                           as quarter,
    month(date_day)                             as month,
    monthname(date_day)                         as month_name,
    dayname(date_day)                           as day_name,
    dayname(date_day) in ('Sat', 'Sun')         as is_weekend
from spine