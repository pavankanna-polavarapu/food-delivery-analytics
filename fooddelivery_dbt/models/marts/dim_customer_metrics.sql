-- Grain: one row per customer with at least one delivered order

select
    customer_id,
    min(order_ts)                                   as first_order_ts,
    max(order_ts)                                   as last_order_ts,
    count(*)                                        as total_delivered_orders,
    sum(total_amount)                               as lifetime_value,
    {{ convert_currency('sum(total_amount)') }}     as lifetime_value_usd,
    datediff('day', min(order_ts), max(order_ts))   as customer_lifespan_days
from {{ ref('fct_orders') }}
where is_delivered
    and customer_id is not null
group by 1